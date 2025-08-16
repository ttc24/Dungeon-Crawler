import copy
import importlib
import json
import logging
import os
import random
import sys
import time
from functools import lru_cache
from gettext import gettext as _
from pathlib import Path

from . import combat as combat_module
from . import data
from . import map as map_module
from . import shop as shop_module
from .combat_log import CombatLog
from .config import config
from .constants import (
    ANNOUNCER_LINES,
    INVALID_KEY_MSG,
    RIDDLES,
    RUN_FILE,
    SAVE_FILE,
    SCORE_FILE,
)
from .core import GameState
from .core.map import GameMap
from .data import FloorDefinition, load_items
from .entities import SKILL_DEFS, Companion, Enemy, Player
from .events import CacheEvent
from .items import Armor, Item, Trinket, Weapon
from .plugins import apply_enemy_plugins, apply_item_plugins
from .quests import EscortNPC, EscortQuest, FetchQuest, HuntQuest
from .rendering import Renderer, render_map_string
from .stats_logger import StatsLogger

logger = logging.getLogger(__name__)

# Mapping of leaderboard sorting options to record keys and sort direction.
# ``True`` indicates descending order.
LEADERBOARD_SORT_KEYS = {
    "score": ("score", True),
    "depth": ("floor_reached", True),
    "time": ("run_duration", False),
}

# ---------------------------------------------------------------------------
# Data loading utilities
# ---------------------------------------------------------------------------
# ``data/enemies.json`` schema (list of dictionaries):
# [
#   {
#     "name": str,
#     "stats": [hp_min, hp_max, atk_min, atk_max, defense],
#     "ability": "optional",
#     "ai": {"aggressive": int, "defensive": int, "unpredictable": int},
#     "traits": [str, ...]
#   },
#   ...
# ]
#
# ``data/bosses.json`` schema:
# [
#   {
#     "name": str,
#     "stats": [hp, atk, defense, credits],
#     "ability": "optional",
#     "loot": [
#       {
#         "name": str,
#         "description": str,
#         "min_damage": int,
#         "max_damage": int,
#         "price": int
#       }
#     ],
#     "ai": {"aggressive": int, "defensive": int, "unpredictable": int},
#     "traits": [str, ...]
#   },
#   ...
# ]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Predefined word lists used for random room name generation. Keeping them at
# module scope avoids recreating the lists on every call to
# ``generate_room_name`` which occurs hundreds of times per floor.
ROOM_NAME_ADJECTIVES = [
    "Collapsed",
    "Echoing",
    "Gloomy",
    "Withered",
    "Fungal",
    "Whispering",
    "Icy",
    "Dust-choked",
    "Ancient",
    "Haunted",
    "Buried",
    "Broken",
    "Wretched",
    "Twisting",
]

ROOM_NAME_NOUNS = [
    "Passage",
    "Fissure",
    "Grotto",
    "Vault",
    "Sanctum",
    "Shrine",
    "Cellar",
    "Refuge",
    "Gallery",
    "Crypt",
    "Atrium",
    "Chapel",
    "Workshop",
    "Quarters",
]


@lru_cache(maxsize=None)
def load_enemies():
    """Load enemy definitions from ``enemies.json``."""
    path = DATA_DIR / "enemies.json"
    with open(path) as f:
        data = json.load(f)
    stats = {}
    abilities = {}
    ai = {}
    traits = {}
    for cfg in data:
        name = cfg["name"]
        stats[name] = tuple(cfg["stats"])
        ability = cfg.get("ability")
        if ability:
            abilities[name] = ability
        if cfg.get("ai"):
            ai[name] = cfg["ai"]
        if cfg.get("traits"):
            traits[name] = cfg["traits"]
    return stats, abilities, ai, traits


@lru_cache(maxsize=None)
def load_bosses():
    """Load boss stats and loot tables from ``bosses.json``."""
    path = DATA_DIR / "bosses.json"
    with open(path) as f:
        data = json.load(f)
    stats = {}
    loot = {}
    ai = {}
    traits = {}
    for cfg in data:
        name = cfg["name"]
        hp, atk, dfs, credits = cfg["stats"]
        stats[name] = (hp, atk, dfs, credits, cfg.get("ability"))
        if "loot" in cfg:
            loot[name] = [Weapon(**item) for item in cfg["loot"]]
        if cfg.get("ai"):
            ai[name] = cfg["ai"]
        if cfg.get("traits"):
            traits[name] = cfg["traits"]
    return stats, loot, ai, traits


ENEMY_STATS, ENEMY_ABILITIES, ENEMY_AI, ENEMY_TRAITS = load_enemies()
BOSS_STATS, BOSS_LOOT, BOSS_AI, BOSS_TRAITS = load_bosses()
apply_enemy_plugins(ENEMY_STATS, ENEMY_ABILITIES, ENEMY_AI, ENEMY_TRAITS)


class FloorHooks:
    """Interface for floor specific hooks.

    Each method receives the current :class:`GameState` and associated
    :class:`~dungeoncrawler.data.FloorDefinition`.
    """

    def on_floor_start(self, state: GameState, floor: FloorDefinition) -> None:
        """Called when a new floor is entered."""

    def on_turn(self, state: GameState, floor: FloorDefinition) -> None:
        """Invoked each turn of the main game loop."""

    def on_objective_check(self, state: GameState, floor: FloorDefinition) -> bool:
        """Return ``True`` if the floor objective has been met."""
        return False

    def on_floor_end(self, state: GameState, floor: FloorDefinition) -> None:
        """Called when leaving a floor."""


def load_hook_modules(paths: list[str]) -> list[FloorHooks]:
    """Import hook modules and instantiate their ``Hooks`` class if present."""

    hooks: list[FloorHooks] = []
    for path in paths:
        try:
            module = importlib.import_module(path)
            hook_cls = getattr(module, "Hooks", None)
            if hook_cls:
                hooks.append(hook_cls())
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to import hook module %s", path)
    return hooks or [FloorHooks()]


def floor_size(floor: int) -> tuple[int, int]:
    """Return map size for a given floor.

    Early floors are intentionally small to ease new players in. Size grows
    gradually until Floor 10 where the dungeon expands sharply.
    """

    if floor == 1:
        return (20, 12)
    if floor == 2:
        return (24, 14)
    if floor < 10:
        width = 28 + 2 * (floor - 3)
        height = 16 + 2 * (floor - 3)
        return (width, height)
    # Dramatic increase from floor 10 onwards
    width = 60 + 4 * (floor - 10)
    height = 40 + 4 * (floor - 10)
    return (width, height)


# Floor specific configuration loaded from data/floors.json


@lru_cache(maxsize=None)
def load_floor_configs():
    """Load per-floor configuration from ``floors.json``."""
    path = DATA_DIR / "floors.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    configs = {}
    for floor, cfg in data.items():
        floor = int(floor)
        # Always compute size programmatically so adjustments in ``floor_size``
        # apply without requiring updates to the JSON data.
        cfg["size"] = tuple(floor_size(floor))

        # ------------------------------------------------------------------
        # Weighted enemy / boss tables
        # ------------------------------------------------------------------
        # Floors can optionally specify enemy or boss collections either as a
        # simple list or as a mapping of ``name -> weight``.  Using a mapping
        # allows individual entries to appear more or less frequently when the
        # dungeon is generated.  To keep selection simple (and easily patchable
        # in tests) we expand the weighted tables into a list "pool" where each
        # name is repeated ``weight`` times.  ``random.choice`` can then be used
        # without the need for ``random.choices`` which is harder to monkeypatch
        # deterministically.

        enemies = cfg.get("enemies", [])
        if isinstance(enemies, dict):
            pool: list[str] = []
            for name, weight in enemies.items():
                pool.extend([name] * max(1, int(weight)))
            cfg["enemy_pool"] = pool
        else:
            # Preserve original list but also expose a pool for weighted picks
            cfg["enemy_pool"] = list(enemies)

        bosses = cfg.get("bosses", [])
        if isinstance(bosses, dict):
            pool: list[str] = []
            for name, weight in bosses.items():
                pool.extend([name] * max(1, int(weight)))
            cfg["boss_pool"] = pool
        else:
            cfg["boss_pool"] = list(bosses)

        # Allow configuration to define multiple boss slots per floor.  Default
        # to a single boss to maintain existing behaviour.
        cfg.setdefault("boss_slots", 1)

        # Event configuration will be filled with defaults during game init
        configs[floor] = cfg
    return configs


class DungeonBase:
    """Core engine for running the dungeon crawler game.

    The class manages dungeon generation, room handling and turn based
    combat.  High level methods like :meth:`generate_dungeon`,
    :meth:`move_player`, :meth:`battle` and :meth:`play_game` orchestrate the
    flow of a game session while utility helpers handle saving progress and
    shop interactions.
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rooms = [[None for __ in range(width)] for __ in range(height)]
        self.room_names = [
            [self.generate_room_name() for __ in range(width)] for __ in range(height)
        ]
        self.visited_rooms = set()
        self.discovered = [[False for __ in range(width)] for __ in range(height)]
        self.visible = [[False for __ in range(width)] for __ in range(height)]
        self.player = None
        self.exit_coords = None
        self.tutorial_complete = False
        self.shop_items, self.rare_loot = load_items()
        apply_item_plugins(self.shop_items)
        self.shop_items.extend(
            [
                Weapon("Rusty Pike", "Barely holds together", 3, 6, 5),
                Item("Mystic Orb", "Glimmers with arcane energy"),
                Weapon("Iron Staff", "Heavy but reliable", 5, 9, 12),
            ]
        )
        self.rare_loot.extend(
            [
                Weapon(
                    "Phantom Blade",
                    "Slices through spirit and bone",
                    12,
                    18,
                    120,
                    "bleed",
                ),
                Item("Elixir of Insight", "Reveals hidden paths"),
            ]
        )
        self.shop_inventory: list[Item] = []
        (
            self.random_events,
            self.random_event_weights,
            self.default_place_counts,
            self.signature_events,
        ) = data.load_event_defs()
        self.riddles = RIDDLES
        self.enemy_stats = ENEMY_STATS
        self.enemy_abilities = ENEMY_ABILITIES
        self.enemy_ai = ENEMY_AI
        self.enemy_traits = ENEMY_TRAITS
        self.boss_stats = BOSS_STATS
        self.boss_loot = BOSS_LOOT
        self.boss_ai = BOSS_AI
        self.boss_traits = BOSS_TRAITS
        # Load a fresh copy of the floor configuration for each game instance
        # so tests that mutate the underlying JSON can observe the changes
        # without leaking state between runs.
        self.floor_configs = copy.deepcopy(load_floor_configs())
        for cfg in self.floor_configs.values():
            cfg.setdefault("events", self.random_events)
            for ev, weight in zip(self.random_events, self.random_event_weights):
                name = ev.__name__.replace("Event", "").lower()
                cfg.setdefault(f"{name}_rate", weight)
        # Tracking for leaderboard entries
        self.run_start = None
        self.seed = None
        # Persistent run statistics including unlocked character options
        self.run_stats = {
            "total_runs": 0,
            "unlocks": {"class": False, "guild": False, "race": False},
            "max_floor": 0,
        }
        if RUN_FILE.exists():
            try:
                with open(RUN_FILE) as f:
                    self.run_stats.update(json.load(f))
            except (IOError, json.JSONDecodeError):
                logger.exception("Failed to load run statistics from %s", RUN_FILE)
        self.total_runs = self.run_stats.get("total_runs", 0)
        self.unlocks = self.run_stats.get(
            "unlocks", {"class": False, "guild": False, "race": False}
        )
        self.max_floor = self.run_stats.get("max_floor", 0)
        self.novice_luck_announced = False
        self.stairs_prompt_shown = False
        self.active_quest = None
        self.last_action: str | None = None
        # Track guild trial completion when present
        self.completed_trials: set[str] = set()
        # Balance metrics logger and combat message buffer
        self.stats_logger = StatsLogger()
        self.combat_log = CombatLog()
        self.messages: list[str] = []
        self.renderer = Renderer()
        # Schedule the first shop to appear on floor 2
        self.next_shop_floor = 2
        self.floor_hooks: list[FloorHooks] = [FloorHooks()]
        self.floor_def: FloorDefinition | None = None
        self.current_floor = 0
        # Track whether late-game scaling has been applied to avoid stacking
        self._tier_two_scaled = False
        self._base_trap_chance = config.trap_chance

    def queue_message(self, text: str, output_func=print):
        """Store ``text`` for later rendering and optionally display it."""

        self.messages.append(text)
        if getattr(self, "combat_log", None) is not None:
            self.combat_log.log(text)
        if output_func:
            output_func(text)
        return text

    def announce(self, msg):
        self.queue_message(_(f"[Announcer] {random.choice(ANNOUNCER_LINES)} {msg}"))

    def _make_state(self, floor: int) -> GameState:
        """Construct a :class:`GameState` snapshot for hooks."""

        gm = GameMap(self.rooms)
        gm.discovered = self.discovered
        gm.visible = self.visible
        return GameState(
            seed=self.seed or 0,
            current_floor=floor,
            player=self.player,
            game_map=gm,
            log=list(self.messages),
            game=self,
        )

    def save_game(self, floor):
        def serialize_item(item):
            if item is None:
                return None
            data = {
                "name": item.name,
                "description": item.description,
                "rarity": getattr(item, "rarity", "common"),
            }
            if isinstance(item, Weapon):
                data.update(
                    {
                        "min_damage": item.min_damage,
                        "max_damage": item.max_damage,
                        "price": item.price,
                        "effect": item.effect,
                    }
                )
            elif isinstance(item, Armor):
                data.update(
                    {
                        "defense": item.defense,
                        "price": item.price,
                        "effect": item.effect,
                    }
                )
            elif isinstance(item, Trinket):
                data.update({"price": item.price, "effect": item.effect})
            return data

        data = {
            "floor": floor,
            "tutorial_complete": self.tutorial_complete,
            "player": {
                "name": self.player.name,
                "level": self.player.level,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "attack_power": self.player.attack_power,
                "xp": self.player.xp,
                "credits": self.player.credits,
                "class": self.player.class_type,
                "stamina": self.player.stamina,
                "temp_strength": getattr(self.player, "temp_strength", 0),
                "temp_intelligence": getattr(self.player, "temp_intelligence", 0),
                "skill_cooldowns": {k: v["cooldown"] for k, v in self.player.skills.items()},
                "guild": self.player.guild,
                "race": self.player.race,
                "inventory": [serialize_item(it) for it in self.player.inventory],
                "weapon": serialize_item(self.player.weapon),
                "armor": serialize_item(self.player.armor),
                "trinket": serialize_item(self.player.trinket),
                "companions": [
                    {"name": c.name, "effect": c.effect} for c in self.player.companions
                ],
                "codex": self.player.codex,
            },
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)
        except IOError:
            logger.exception("Failed to save game to %s", SAVE_FILE)
            self.renderer.show_message(_("Failed to save game."))

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE) as f:
                    data = json.load(f)
            except (IOError, json.JSONDecodeError):
                return 1
            self.tutorial_complete = data.get("tutorial_complete", False)
            self.player = Player(data["player"]["name"], data["player"].get("class", "Novice"))
            p = data["player"]
            self.player.level = p["level"]
            self.player.health = p["health"]
            self.player.max_health = p["max_health"]
            self.player.attack_power = p["attack_power"]
            self.player.xp = p["xp"]
            self.player.credits = p["credits"]
            self.player.stamina = p.get("stamina", self.player.max_stamina)
            self.player.temp_strength = p.get("temp_strength", 0)
            self.player.temp_intelligence = p.get("temp_intelligence", 0)
            cooldowns = p.get("skill_cooldowns", {})
            for k, v in cooldowns.items():
                if k in self.player.skills:
                    self.player.skills[k]["cooldown"] = v
            self.player.guild = p.get("guild")
            self.player.race = p.get("race")
            for item_data in p.get("inventory", []):
                if "min_damage" in item_data:
                    item = Weapon(
                        item_data["name"],
                        item_data["description"],
                        item_data["min_damage"],
                        item_data["max_damage"],
                        item_data.get("price", 50),
                        item_data.get("rarity", "common"),
                        item_data.get("effect"),
                    )
                elif "defense" in item_data:
                    item = Armor(
                        item_data["name"],
                        item_data["description"],
                        item_data["defense"],
                        item_data.get("price", 40),
                        item_data.get("rarity", "common"),
                        item_data.get("effect"),
                    )
                elif "effect" in item_data and item_data.get("price") is not None:
                    item = Trinket(
                        item_data["name"],
                        item_data["description"],
                        item_data.get("effect"),
                        item_data.get("price", 30),
                        item_data.get("rarity", "common"),
                    )
                else:
                    item = Item(item_data["name"], item_data["description"])
                self.player.inventory.append(item)

            weapon_data = p.get("weapon")
            if weapon_data:
                self.player.weapon = Weapon(
                    weapon_data["name"],
                    weapon_data["description"],
                    weapon_data["min_damage"],
                    weapon_data["max_damage"],
                    weapon_data.get("price", 50),
                    weapon_data.get("rarity", "common"),
                    weapon_data.get("effect"),
                )
            armor_data = p.get("armor")
            if armor_data:
                self.player.armor = Armor(
                    armor_data["name"],
                    armor_data["description"],
                    armor_data["defense"],
                    armor_data.get("price", 40),
                    armor_data.get("rarity", "common"),
                    armor_data.get("effect"),
                )
            trinket_data = p.get("trinket")
            if trinket_data:
                self.player.trinket = Trinket(
                    trinket_data["name"],
                    trinket_data["description"],
                    trinket_data.get("effect"),
                    trinket_data.get("price", 30),
                    trinket_data.get("rarity", "common"),
                )

            for comp_data in p.get("companions", []):
                self.player.companions.append(Companion(comp_data["name"], comp_data["effect"]))
            self.player.codex = p.get("codex", [])

            return data.get("floor", 1)
        return 1

    def save_run_stats(self):
        """Persist total run count and unlocked character options."""

        self.run_stats["total_runs"] = self.total_runs
        self.run_stats["unlocks"] = self.unlocks
        self.run_stats["max_floor"] = self.max_floor
        try:
            with open(RUN_FILE, "w") as f:
                json.dump(self.run_stats, f)
        except IOError:
            logger.exception("Failed to save run statistics to %s", RUN_FILE)
            self.renderer.show_message(_("Failed to update run statistics."))

    def record_score(self, floor):
        """Persist the current run to the leaderboard file and display it."""
        # Update total run count used for first-run bonuses
        self.total_runs += 1
        self.save_run_stats()

        records = []
        if os.path.exists(SCORE_FILE):
            try:
                with open(SCORE_FILE) as f:
                    records = json.load(f)
            except (IOError, json.JSONDecodeError):
                records = []

        now = time.time()
        duration = now - self.run_start if self.run_start else 0
        epitaph = f"Fell on Floor {floor} to '{self.player.cause_of_death or 'Unknown'}'"
        breakdown = self.player.get_score_breakdown()

        self.renderer.show_message(_(f"Final Score: {breakdown['total']}"))
        for line in self.player.format_score_breakdown(breakdown):
            self.renderer.show_message(line)

        records.append(
            {
                "player_name": self.player.name,
                "score": breakdown["total"],
                "breakdown": breakdown,
                "floor_reached": floor,
                "run_duration": duration,
                "seed": self.seed,
                "epitaph": epitaph,
                "timestamp": now,
            }
        )
        # Keep the last 100 entries to prevent the file from growing indefinitely.
        records = records[-100:]
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump(records, f, indent=2)
        except IOError:
            return

        # Use a dummy input function when running in a non-interactive
        # environment so tests do not block waiting for keyboard input.
        input_func = input if sys.stdin.isatty() else (lambda _: "1")
        try:
            self.view_leaderboard(records, input_func=input_func)
        except (OSError, EOFError):
            # ``input`` may still fail when stdin is redirected; simply skip
            # showing the interactive leaderboard in that case.
            pass

    def view_leaderboard(self, records=None, input_func=input, sort_by: str = "score"):
        """Display leaderboard entries stored on disk.

        Parameters
        ----------
        sort_by:
            Determines the ranking metric. Accepts ``"score"``, ``"depth"``
            or ``"time"``. Defaults to ``"score"``.

        The interactive portion asking the player to choose a class is skipped
        when no player is set or when ``input_func`` cannot obtain input.  This
        prevents tests from hanging waiting for user input.
        """

        if records is None:
            records = []
            if os.path.exists(SCORE_FILE):
                try:
                    with open(SCORE_FILE) as f:
                        records = json.load(f)
                except (IOError, json.JSONDecodeError):
                    records = []

        key, reverse = LEADERBOARD_SORT_KEYS.get(sort_by, LEADERBOARD_SORT_KEYS["score"])
        records = sorted(records, key=lambda x: x.get(key, 0), reverse=reverse)[:10]

        print(_("-- Leaderboard --"))
        if not records:
            print(_("No scores yet."))
        else:
            for r in records:
                print(
                    _(
                        f"{r.get('player_name', '?')}: {r.get('score', 0)} "
                        f"(Floor {r.get('floor_reached', '?')}, "
                        f"{r.get('run_duration', 0):.0f}s, Seed {r.get('seed', '?')}) "
                        f"{r.get('epitaph', '')}"
                    )
                )

        # If no player is present there is nothing further to do – the
        # leaderboard was displayed solely for informational purposes.
        if self.player is None:
            return

        # Prompt for a class if the player has not yet chosen one.
        self.offer_class(input_func=input_func)

    def offer_class(self, input_func=input):
        """Allow the player to choose a class.

        The choice is permanent and only offered on floor 1 while the player is
        still a Novice. A short description for each option acts as a tooltip
        and the currently available stamina-based skills are shown.
        """

        if self.current_floor != 1:
            return
        if not self.unlocks.get("class"):
            self.unlocks["class"] = True
            self.save_run_stats()
        if self.player.class_type != "Novice":
            return

        print(_("It's time to choose your class! This choice is permanent."))
        classes = {
            "1": ("Warrior", _("Balanced fighter")),
            "2": ("Mage", _("Master of spells")),
            "3": ("Rogue", _("Stealthy attacker")),
            "4": ("Cleric", _("Holy healer")),
            "5": ("Barbarian", _("Brutal strength")),
            "6": ("Ranger", _("Skilled hunter")),
            "7": ("Druid", _("Nature's guardian")),
            "8": ("Sorcerer", _("Chaotic caster")),
            "9": ("Monk", _("Disciplined striker")),
            "10": ("Warlock", _("Pact magic")),
            "11": ("Necromancer", _("Master of the dead")),
            "12": ("Shaman", _("Spiritual guide")),
            "13": ("Alchemist", _("Potion expert")),
        }
        names = {v[0].lower(): k for k, v in classes.items()}
        skill_tip = ", ".join(f"{s['name']} ({s['cost']} stamina)" for s in SKILL_DEFS)
        for key, (name, desc) in classes.items():
            print(_(f"{key}. {name} - {desc}"))
        print(_(f"Skills: {skill_tip}"))

        aliases = {"wiz": "mage"}

        while True:
            try:
                raw = input_func(_("Class: ")).strip().lower()
            except (EOFError, OSError):
                return
            choice = None
            if raw.isdigit() and raw in classes:
                choice = raw
            else:
                key = aliases.get(raw, raw)
                if key in names:
                    choice = names[key]
            if choice is None:
                print(_("Please enter a number (1–13) or a valid class name."))
                continue
            self.player.choose_class(classes[choice][0])
            break

    def offer_guild(self, input_func=None):
        if self.current_floor != 2:
            return
        if not self.unlocks.get("guild"):
            self.unlocks["guild"] = True
            self.save_run_stats()
        if self.player.guild:
            return
        if input_func is None:
            input_func = input
        print(_("Guilds now accept new members! This choice is permanent."))
        guilds = {
            "1": ("Warriors' Guild", _("Bonus Health")),
            "2": ("Mages' Guild", _("Bonus Attack")),
            "3": ("Rogues' Guild", _("Faster Skills")),
            "4": ("Healers' Circle", _("Extra Vitality")),
            "5": ("Shadow Brotherhood", _("Heavy Strikes")),
            "6": ("Arcane Order", _("Arcane Mastery")),
        }
        skill_tip = ", ".join(f"{s['name']} ({s['cost']} stamina)" for s in SKILL_DEFS)
        for key, (name, desc) in guilds.items():
            print(_(f"{key}. {name} - {desc}"))
        print(_(f"Skills: {skill_tip}"))
        choice = input_func(_("Join which guild? (1-6 or skip): "))
        if choice in guilds:
            self.player.join_guild(guilds[choice][0])

    def offer_race(self, input_func=None):
        if self.current_floor != 3:
            return
        if not self.unlocks.get("race"):
            self.unlocks["race"] = True
            self.save_run_stats()
        if self.player.race:
            return
        if input_func is None:
            input_func = input
        print(_("New races are available to you! This choice is permanent."))
        races = {
            "1": ("Human", _("Versatile")),
            "2": ("Elf", _("Graceful")),
            "3": ("Dwarf", _("Stout")),
            "4": ("Orc", _("Savage")),
            "5": ("Gnome", _("Clever")),
            "6": ("Tiefling", _("Fiendish")),
            "7": ("Dragonborn", _("Draconic")),
            "8": ("Goblin", _("Sneaky")),
        }
        skill_tip = ", ".join(f"{s['name']} ({s['cost']} stamina)" for s in SKILL_DEFS)
        for key, (name, desc) in races.items():
            print(_(f"{key}. {name} - {desc}"))
        print(_(f"Skills: {skill_tip}"))
        choice = input_func(_("Choose your race: "))
        race = races.get(choice)
        if race:
            self.player.choose_race(race[0])

    def generate_room_name(self, room_type=None):
        names = {
            "Treasure": "Glittering Vault",
            "Trap": "Booby-Trapped Passage",
            "Enemy": "Cursed Hall",
            "Exit": "Sealed Gate",
            "Key": "Hidden Niche",
            "Sanctuary": "Sacred Sanctuary",
            "Empty": "Silent Chamber",
        }

        if room_type in names:
            return names[room_type]

        return f"{random.choice(ROOM_NAME_ADJECTIVES)} {random.choice(ROOM_NAME_NOUNS)}"

    def generate_dungeon(self, floor=1):
        """Generate the dungeon layout for ``floor`` and persist progress.

        The original implementation simply delegated to
        :mod:`dungeoncrawler.map`.  To support automatic saving between floors we
        now hook in a call to :meth:`save_game` after generation.  This mirrors
        how the interactive game behaves and ensures the tests have access to a
        freshly saved state whenever a new floor is created.
        """

        # Apply difficulty scaling when the player reaches the second tier of
        # the dungeon.  This boosts enemy health and damage to keep later
        # floors challenging.  Tests can disable this behaviour by enabling
        # the ``debug`` flag in the configuration.
        if floor >= 10 and not self._tier_two_scaled and not config.enable_debug:
            config.enemy_hp_mult += 0.15
            config.enemy_dmg_mult += 0.10
            self._tier_two_scaled = True

        # Apply high floor debuffs
        config.trap_chance = self._base_trap_chance
        if floor >= 11:
            config.trap_chance += 0.2
        self.player.heal_multiplier = 0.5 if floor >= 10 else 1.0
        if floor >= 10:
            # A sandstorm blankets the high floors, limiting sight to four tiles.
            # Previous logic imposed an additional visibility penalty from
            # floor 12 onward, but the new design keeps vision consistent
            # across all later floors.
            self.player.vision = 4
        else:
            self.player.vision = 6 if floor == 1 else 3 + floor // 2

        map_module.generate_dungeon(self, floor)
        self.generate_quest(floor)
        # Persist progress so players can safely quit between floors
        self.save_game(floor)

    def generate_quest(self, floor):
        """Create a simple quest for the current floor."""

        self.active_quest = None
        start = (self.player.x, self.player.y)
        empty = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.rooms[y][x] == "Empty"
        ]
        if not empty:
            return
        qtype = random.choice(["fetch", "hunt", "escort"])
        random.shuffle(empty)
        if qtype == "fetch":
            item = Item("Ancient Relic", "A quest item")
            candidates = [
                pos for pos in empty if abs(pos[0] - start[0]) + abs(pos[1] - start[1]) <= 15
            ]
            loc = candidates[0] if candidates else empty[0]
            self.rooms[loc[1]][loc[0]] = [CacheEvent(), item]
            self.active_quest = FetchQuest(
                item,
                loc,
                reward=40,
                flavor=_("A whisper speaks of a hidden cache."),
            )
        elif qtype == "hunt":
            name = random.choice(list(self.enemy_stats.keys()))
            hp_min, hp_max, atk_min, atk_max, defense = self.enemy_stats[name]
            enemy = Enemy(
                name,
                hp_max + floor * 2,
                atk_max + floor * 2,
                defense + floor // 2,
                random.randint(30, 60),
                traits=self.enemy_traits.get(name),
            )
            enemy.xp = max(5, (enemy.health + enemy.attack_power + enemy.defense) // 15)
            loc = empty[0]
            enemy.x, enemy.y = loc
            self.rooms[loc[1]][loc[0]] = enemy
            self.active_quest = HuntQuest(
                enemy,
                reward=60,
                flavor=_("A bounty is placed on a fearsome foe."),
            )
        else:
            npc = EscortNPC(_("Lost Traveler"))
            loc = empty[0]
            npc.x, npc.y = loc
            self.rooms[loc[1]][loc[0]] = npc
            self.active_quest = EscortQuest(
                npc,
                reward=50,
                flavor=_("A traveler seeks safe passage to the exit."),
            )

    def check_quest_progress(self):
        """Update and resolve the active quest."""

        quest = self.active_quest
        if not quest:
            return
        if isinstance(quest, FetchQuest):
            if not quest.hint_given and not quest.is_complete(self):
                px, py = self.player.x, self.player.y
                dist = abs(px - quest.location[0]) + abs(py - quest.location[1])
                if dist <= 5:
                    print(_("You notice faint footprints nearby."))
                    quest.hint_given = True
            if quest.is_complete(self):
                print(_("Quest complete!"))
                self.player.credits += quest.reward
                self.active_quest = None
        elif isinstance(quest, HuntQuest):
            if quest.is_complete(self):
                print(_("Quest complete!"))
                self.player.credits += quest.reward
                self.active_quest = None
        elif isinstance(quest, EscortQuest):
            npc = quest.npc
            if not npc.following:
                dist = abs(npc.x - self.player.x) + abs(npc.y - self.player.y)
                if dist <= 5:
                    step_x = 1 if self.player.x > npc.x else -1 if self.player.x < npc.x else 0
                    step_y = 1 if self.player.y > npc.y else -1 if self.player.y < npc.y else 0
                    self.rooms[npc.y][npc.x] = "Empty"
                    npc.x += step_x
                    npc.y += step_y
                    if (npc.x, npc.y) == (self.player.x, self.player.y):
                        npc.following = True
                    else:
                        self.rooms[npc.y][npc.x] = npc
            else:
                npc.x, npc.y = self.player.x, self.player.y
            if quest.is_complete(self):
                print(_("Quest complete!"))
                self.player.credits += quest.reward
                self.active_quest = None

    def play_game(self) -> None:
        """Run the main game loop until the player quits or dies."""

        if self.player is None:
            floor = self.load_game()
            if self.player:
                cont = input(_("Continue your last adventure? (y/n): "))
                if cont.lower() != "y":
                    self.player = None
                    floor = 1
        else:
            floor = 1
        if self.player is None:
            raise ValueError("Player must be created before starting the game.")
        # Begin a new run with a fresh seed and timestamp
        self.seed = random.randrange(2**32)
        random.seed(self.seed)
        self.run_start = time.time()
        self.renderer.show_message(_("Welcome to Dungeon Crawler!"))
        while self.player.is_alive() and floor <= 18:
            self.renderer.show_message(_(f"===== Entering Floor {floor} ====="))
            self.generate_dungeon(floor)
            self.stats_logger.start_floor(self, floor)
            if floor == 1:
                self._foreshadow(floor)
            self.trigger_floor_event(floor)

            self.floor_def = data.get_floor(floor)
            self.floor_hooks = load_hook_modules(self.floor_def.hooks if self.floor_def else [])
            state = self._make_state(floor)
            for hook in self.floor_hooks:
                hook.on_floor_start(state, self.floor_def)

            while self.player.is_alive():
                self.renderer.show_message(
                    _(
                        f"Position: ({self.player.x}, {self.player.y}) - "
                        f"{self.room_names[self.player.y][self.player.x]}"
                    )
                )
                self.renderer.show_status(self)
                if self.player.guild:
                    self.renderer.show_message(_(f"Guild: {self.player.guild}"))
                if self.player.race:
                    self.renderer.show_message(_(f"Race: {self.player.race}"))
                if self.active_quest:
                    self.renderer.show_message(_(f"Quest: {self.active_quest.status(self)}"))
                else:
                    self.renderer.show_message(_("Quest: None"))
                self.renderer.show_message(
                    _(
                        "0. Wait 1. Move Left 2. Move Right 3. Move Up 4. Move Down "
                        "5. Visit Shop 6. Inventory 7. Quit 8. Show Map 9. View Leaderboard"
                    )
                )
                choice = input(_("Action: "))
                if not self.handle_input(choice):
                    self.stats_logger.finalize(self, self.player.cause_of_death or "Quit")
                    return

                floor, continue_floor = self.process_turn(floor)
                if continue_floor is None:
                    self.stats_logger.finalize(self, self.player.cause_of_death or "Quit")
                    return
                if not continue_floor:
                    end_state = self._make_state(floor - 1)
                    for hook in self.floor_hooks:
                        hook.on_floor_end(end_state, self.floor_def)
                    self.stats_logger.end_floor(self)
                    break

        self.renderer.show_message(_("You have died. Game Over!"))
        self.renderer.show_message(
            _(f"Fell on Floor {floor} to '{self.player.cause_of_death or 'Unknown'}'")
        )
        self.record_score(floor)
        self.stats_logger.finalize(self, self.player.cause_of_death or "Unknown")
        if os.path.exists(SAVE_FILE):
            try:
                os.remove(SAVE_FILE)
            except OSError:
                logger.exception("Failed to remove save file %s", SAVE_FILE)

    def handle_input(self, choice: str) -> bool:
        """Handle a menu ``choice`` from the player.

        Returns ``False`` if the player chooses to quit the game, otherwise
        returns ``True`` to continue playing.
        """

        if choice == "0":
            self.player.wait()
            self.last_action = "wait"
        elif choice == "1":
            self.move_player("left")
            self.last_action = "move"
        elif choice == "2":
            self.move_player("right")
            self.last_action = "move"
        elif choice == "3":
            self.move_player("up")
            self.last_action = "move"
        elif choice == "4":
            self.move_player("down")
            self.last_action = "move"
        elif choice == "5":
            self.shop()
            self.last_action = "other"
        elif choice == "6":
            self.show_inventory()
            self.last_action = "other"
        elif choice == "7":
            self.renderer.show_message(_("Thanks for playing!"))
            return False
        elif choice == "8":
            self.view_map()
            self.last_action = "other"
        elif choice == "9":
            self.view_leaderboard()
            self.last_action = "other"
        elif config.enable_debug and choice.startswith(":god"):
            self.god_mode(choice)
        elif config.enable_debug and choice.startswith(":sim"):
            self.simulate(command=choice)
        elif choice == ":codex":
            self.show_codex()
        else:
            self.renderer.show_message(_(INVALID_KEY_MSG))
        return True

    def god_mode(self, command: str) -> None:
        """Execute debug commands when ``config.enable_debug`` is True."""

        parts = command.split()
        if len(parts) < 2:
            self.renderer.show_message(
                self.queue_message(_("Usage: :god <spawn|teleport|set>"), output_func=None)
            )
            return

        action = parts[1]
        if action == "spawn" and len(parts) >= 3:
            item_name = " ".join(parts[2:])
            item = Item(item_name, "Debug spawn")
            self.player.inventory.append(item)
            msg = _(f"Spawned {item_name}")
            self.renderer.show_message(self.queue_message(msg, output_func=None))
        elif action == "teleport" and len(parts) >= 3:
            try:
                floor = int(parts[2])
            except ValueError:
                self.renderer.show_message(self.queue_message(_("Invalid floor"), output_func=None))
                return
            self.current_floor = floor
            self.generate_dungeon(floor)
            msg = _(f"Teleported to floor {floor}")
            self.renderer.show_message(self.queue_message(msg, output_func=None))
        elif action == "set" and len(parts) >= 4:
            stat, value = parts[2], parts[3]
            if hasattr(self.player, stat):
                attr = getattr(self.player, stat)
                try:
                    cast_value = type(attr)(value)
                except (TypeError, ValueError):
                    self.renderer.show_message(
                        self.queue_message(_("Invalid value"), output_func=None)
                    )
                    return
                setattr(self.player, stat, cast_value)
                msg = _(f"Set {stat} to {cast_value}")
                self.renderer.show_message(self.queue_message(msg, output_func=None))
            else:
                self.renderer.show_message(self.queue_message(_("Unknown stat"), output_func=None))
        else:
            self.renderer.show_message(
                self.queue_message(_("Invalid god command"), output_func=None)
            )

    def simulate(self, command: str) -> None:
        """Run automated combat simulations.

        Usage: ``:sim <enemy> <runs>``
        """
        parts = command.split()
        if len(parts) < 3:
            self.renderer.show_message(
                self.queue_message(_("Usage: :sim <enemy> <runs>"), output_func=None)
            )
            return
        enemy_name = parts[1]
        try:
            runs = int(parts[2])
        except ValueError:
            self.renderer.show_message(self.queue_message(_("Invalid run count"), output_func=None))
            return
        from .sim import simulate_battles

        stats = simulate_battles(enemy_name, runs, seed=42)
        msg = _(f"Winrate: {stats['winrate']:.2%} | Avg TTK: {stats['avg_turns']:.2f}")
        self.renderer.show_message(self.queue_message(msg, output_func=None))

    def show_codex(self, output_func=print):
        if not self.player.codex:
            output_func(_("Codex is empty."))
            return
        output_func(_("Codex:"))
        for entry in self.player.codex:
            output_func(f"- {entry}")

    def process_turn(self, floor: int):
        """Handle end-of-turn effects and floor completion checks.

        Returns a tuple of ``(floor, status)`` where ``status`` is ``True`` to
        continue on the current floor, ``False`` to advance to the next floor
        and ``None`` if the player chose to exit the game.
        """

        state = self._make_state(floor)
        for hook in self.floor_hooks:
            hook.on_turn(state, self.floor_def)

        if self.player.level >= 5 and self.player.health < self.player.max_health:
            self.player.health += 1

        return self.check_floor_completion(floor)

    def _foreshadow(self, floor: int) -> None:
        """Print a hint about upcoming features for the next floor."""

        if floor == 1:
            self.renderer.show_message(_("Rumor has it new classes await ahead."))
        elif floor == 2:
            self.renderer.show_message(_("Guild banners flutter somewhere below."))
        elif floor == 3:
            self.renderer.show_message(_("Whispers speak of diverse races deeper within."))

    def check_floor_completion(self, floor: int):
        """Determine if the current floor has been completed.

        Returns ``(new_floor, status)`` similar to :meth:`process_turn`.
        """

        state = self._make_state(floor)
        for hook in self.floor_hooks:
            if hook.on_objective_check(state, self.floor_def):
                floor += 1
                self.player.temp_strength = 0
                self.player.temp_intelligence = 0
                self.save_game(floor)
                self._foreshadow(floor)
                return floor, False

        if (
            self.player.x == self.exit_coords[0]
            and self.player.y == self.exit_coords[1]
            and self.player.has_item("Key")
        ):
            self.renderer.show_message(_("You reach the Sealed Gate."))
            if floor == 9:
                prompt = _("Descend to the final floor or retire? (d/r): ")
                proceed = input(prompt).strip().lower()
                if proceed.startswith("d"):
                    floor += 1
                    self.player.temp_strength = 0
                    self.player.temp_intelligence = 0
                    self.save_game(floor)
                    self._foreshadow(floor)
                    return floor, False
                self.renderer.show_message(_("You retire from the dungeon."))
            elif floor == 18:
                keys = sum(
                    1 for item in self.player.inventory if getattr(item, "name", "") == "Key"
                )
                slots = self.floor_configs.get(18, {}).get("boss_slots", 1)
                if keys < slots:
                    proceed = (
                        input(_("Exit the dungeon or continue fighting? (y/n): ")).strip().lower()
                    )
                    if proceed != "y":
                        return floor, True
                self.player.score_buff += keys * 100
                self.record_score(floor)
                if os.path.exists(SAVE_FILE):
                    try:
                        os.remove(SAVE_FILE)
                    except OSError:
                        logger.exception("Failed to remove save file %s", SAVE_FILE)
                return floor, None
            else:
                proceed = input(_("Would you like to descend to the next floor? (y/n): ")).lower()
                if proceed == "y":
                    floor += 1
                    # Reset temporary floor buffs
                    self.player.temp_strength = 0
                    self.player.temp_intelligence = 0
                    self.save_game(floor)
                    self._foreshadow(floor)
                    return floor, False
                self.renderer.show_message(_("You chose to exit the dungeon."))

            self.record_score(floor)
            if os.path.exists(SAVE_FILE):
                try:
                    os.remove(SAVE_FILE)
                except OSError:
                    logger.exception("Failed to remove save file %s", SAVE_FILE)
            return floor, None

        return floor, True

    def move_player(self, direction):
        prev = (self.player.x, self.player.y)
        msg = map_module.move_player(self, direction)
        if (self.player.x, self.player.y) != prev:
            self.stats_logger.record_move()
            self.player.regen_stamina(20)
        return msg

    def render_map(self):
        self.renderer.draw_map(render_map_string(self))

    def view_map(self, input_func=None):
        if input_func is None:
            input_func = input if sys.stdin.isatty() else (lambda _: "")
        while True:
            self.render_map()
            response = input_func(_("Press '?' for legend, any other key to exit: ")).strip()
            if response == "?":
                self.renderer.toggle_legend()
                continue
            break

    def handle_room(self, x, y):
        map_module.handle_room(self, x, y)

    def battle(self, enemy):
        combat_module.battle(self, enemy)

    def audience_gift(self):
        if random.random() < 0.1:
            self.renderer.show_message(
                _("A package falls from above! It's a gift from the audience.")
            )
            if random.random() < 0.5:
                item = Item("Health Potion", "Restores 20 health")
                self.player.collect_item(item)
                self.renderer.show_message(_(f"You received a {item.name}."))
                self.announce(f"{self.player.name} gains a helpful item!")
            else:
                damage = random.randint(5, 15)
                self.player.take_damage(damage, source="Audience Gift")
                self.renderer.show_message(_(f"Uh-oh! It explodes and deals {damage} damage."))
                self.announce("The crowd loves a good prank!")

    def grant_inspiration(self, turns=3):
        """Give the player a temporary inspire buff."""
        self.player.status_effects["inspire"] = turns

    def shop(self, input_func=input, output_func=print):
        shop_module.shop(self, input_func=input_func, output_func=output_func)

    def restock_shop(self, count: int = 4) -> None:
        """Refresh the available shop inventory."""

        if not self.shop_items:
            self.shop_inventory = []
            return
        base = self.shop_items[:1]
        pool = self.shop_items[1:]
        k = min(max(0, count - len(base)), len(pool))
        self.shop_inventory = base + random.sample(pool, k)

    def get_sale_price(self, item):
        return shop_module.get_sale_price(item)

    def sell_items(self, input_func=input, output_func=print):
        shop_module.sell_items(self, input_func=input_func, output_func=output_func)

    def show_inventory(self, input_func=input, output_func=print):
        shop_module.show_inventory(self, input_func=input_func, output_func=output_func)

    def riddle_challenge(self):
        """Present the player with a riddle for a potential reward."""
        riddle, answer = random.choice(self.riddles)
        print(_("A sage poses a riddle:\n") + riddle)
        response = input(_("Answer: ")).strip().lower()
        if response == answer:
            reward = 50
            print(_(f"Correct! You receive {reward} credits."))
            self.player.credits += reward
        else:
            print(_("Incorrect! The sage vanishes in disappointment."))

    def trigger_random_event(self, floor):
        """Randomly select and trigger an event for ``floor``."""
        cfg = self.floor_configs.get(floor, {})
        events = cfg.get("events")
        if events:
            # ``random.choice`` is used instead of ``random.choices`` so tests can
            # deterministically patch the selection logic.  To preserve weighted
            # probabilities we expand the events list based on their configured
            # weights and choose from that.
            weighted_events = []
            for ev in events:
                name = ev.__name__.replace("Event", "").lower()
                weight = cfg.get(f"{name}_rate", 1.0)
                # ensure each event appears at least once to keep it selectable
                count = max(1, int(weight * 100))
                weighted_events.extend([ev] * count)

            # Fall back to the unweighted list if weights produced an empty pool
            pool = weighted_events or events
            event_cls = random.choice(pool)
            event = event_cls()
            event.trigger(self)

    def trigger_signature_event(self) -> None:
        """Select and trigger one signature event from the curated pool."""
        if not self.signature_events:
            return
        event_cls = random.choice(self.signature_events)
        event_cls().trigger(self)

    # Floor-specific events keep gameplay varied without hardcoding logic in
    # play_game. Additional floors can be added here easily.
    def trigger_floor_event(self, floor):
        self.current_floor = floor
        if floor > self.max_floor:
            self.max_floor = floor
            self.run_stats["max_floor"] = self.max_floor
            self.save_run_stats()
        if floor >= self.next_shop_floor:
            print(_("A traveling merchant sets up shop."))
            self.restock_shop()
            self.shop()
            self.next_shop_floor = floor + random.randint(2, 3)

        events = {
            1: self._floor_one_event,
            2: self._floor_two_event,
            3: self._floor_three_event,
            4: self._floor_four_event,
            5: self._floor_five_event,
            6: self._floor_six_event,
            7: self._floor_seven_event,
            8: self._floor_eight_event,
            9: self._floor_nine_event,
            10: self._floor_ten_event,
            11: self._floor_eleven_event,
            12: self._floor_twelve_event,
            13: self._floor_thirteen_event,
            14: self._floor_fourteen_event,
            15: self._floor_fifteen_event,
        }
        if floor in events:
            events[floor]()

    def _floor_one_event(self):
        print(_("The crowd roars as you step into the arena for the first time."))
        self.offer_class()
        self.trigger_signature_event()

    def _floor_two_event(self):
        self.offer_guild()
        self.trigger_signature_event()

    def _floor_three_event(self):
        self.offer_race()
        self.trigger_signature_event()

    def _floor_four_event(self):
        self.trigger_signature_event()

    def _floor_five_event(self):
        self.trigger_signature_event()

    def _floor_six_event(self):
        self.trigger_signature_event()

    def _floor_seven_event(self):
        self.trigger_signature_event()

    def _floor_eight_event(self):
        self.trigger_signature_event()

    def _floor_nine_event(self):
        self.trigger_signature_event()

    def _floor_ten_event(self):
        self.trigger_signature_event()

    def _floor_eleven_event(self):
        self.trigger_signature_event()

    def _floor_twelve_event(self):
        self.trigger_signature_event()

    def _floor_thirteen_event(self):
        self.trigger_signature_event()

    def _floor_fourteen_event(self):
        self.trigger_signature_event()

    def _floor_fifteen_event(self):
        self.trigger_signature_event()
