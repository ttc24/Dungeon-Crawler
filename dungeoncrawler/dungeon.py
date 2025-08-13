import json
import os
import random
import time
from functools import lru_cache
from gettext import gettext as _
from pathlib import Path

from . import combat as combat_module
from . import map as map_module
from . import shop as shop_module
from .config import config
from .constants import (
    ANNOUNCER_LINES,
    INVALID_KEY_MSG,
    RIDDLES,
    RUN_FILE,
    SAVE_FILE,
    SCORE_FILE,
)
from .data import load_event_defs, load_items
from .entities import Companion, Enemy, Player
from .events import (
    CacheEvent,
    FountainEvent,
    HazardEvent,
    LoreNoteEvent,
    MiniQuestHookEvent,
    ShrineEvent,
    TrapEvent,
)
from .items import Item, Weapon
from .plugins import apply_enemy_plugins, apply_item_plugins
from .quests import EscortNPC, EscortQuest, FetchQuest, HuntQuest
from .rendering import Renderer, render_map_string
from .stats_logger import StatsLogger

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
#     "stats": [hp, atk, defense, gold],
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
        hp, atk, dfs, gold = cfg["stats"]
        stats[name] = (hp, atk, dfs, gold, cfg.get("ability"))
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
        # Event configuration will be filled with defaults during game init
        configs[floor] = cfg
    return configs


FLOOR_CONFIGS = load_floor_configs()


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
        (
            self.random_events,
            self.random_event_weights,
            self.default_place_counts,
        ) = load_event_defs()
        self.riddles = RIDDLES
        self.enemy_stats = ENEMY_STATS
        self.enemy_abilities = ENEMY_ABILITIES
        self.enemy_ai = ENEMY_AI
        self.enemy_traits = ENEMY_TRAITS
        self.boss_stats = BOSS_STATS
        self.boss_loot = BOSS_LOOT
        self.boss_ai = BOSS_AI
        self.boss_traits = BOSS_TRAITS
        self.floor_configs = FLOOR_CONFIGS
        for cfg in self.floor_configs.values():
            cfg.setdefault("events", self.random_events)
            for ev, weight in zip(self.random_events, self.random_event_weights):
                name = ev.__name__.replace("Event", "").lower()
                cfg.setdefault(f"{name}_rate", weight)
        # Tracking for leaderboard entries
        self.run_start = None
        self.seed = None
        # Persistent run statistics used for "Novice's Luck"
        self.total_runs = 0
        if RUN_FILE.exists():
            try:
                with open(RUN_FILE) as f:
                    self.total_runs = json.load(f).get("total_runs", 0)
            except (IOError, json.JSONDecodeError):
                self.total_runs = 0
        self.novice_luck_announced = False
        self.stairs_prompt_shown = False
        self.active_quest = None
        # Balance metrics logger
        self.stats_logger = StatsLogger()
        self.messages: list[str] = []
        self.renderer = Renderer()

    def queue_message(self, text: str):
        """Store ``text`` for later rendering and return it."""

        self.messages.append(text)
        return text

    def announce(self, msg):
        self.queue_message(_(f"[Announcer] {random.choice(ANNOUNCER_LINES)} {msg}"))

    def save_game(self, floor):
        def serialize_item(item):
            if item is None:
                return None
            data = {"name": item.name, "description": item.description}
            if isinstance(item, Weapon):
                data.update(
                    {
                        "min_damage": item.min_damage,
                        "max_damage": item.max_damage,
                        "price": item.price,
                        "effect": item.effect,
                    }
                )
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
                "gold": self.player.gold,
                "class": self.player.class_type,
                "stamina": self.player.stamina,
                "temp_strength": getattr(self.player, "temp_strength", 0),
                "temp_intelligence": getattr(self.player, "temp_intelligence", 0),
                "skill_cooldowns": {k: v["cooldown"] for k, v in self.player.skills.items()},
                "guild": self.player.guild,
                "race": self.player.race,
                "inventory": [serialize_item(it) for it in self.player.inventory],
                "weapon": serialize_item(self.player.weapon),
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
            pass

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
            self.player.gold = p["gold"]
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
                    )
                    item.effect = item_data.get("effect")
                else:
                    item = Item(item_data["name"], item_data["description"])
                self.player.inventory.append(item)

            weapon_data = p.get("weapon")
            if weapon_data:
                weapon = Weapon(
                    weapon_data["name"],
                    weapon_data["description"],
                    weapon_data["min_damage"],
                    weapon_data["max_damage"],
                    weapon_data.get("price", 50),
                )
                weapon.effect = weapon_data.get("effect")
                self.player.weapon = weapon

            for comp_data in p.get("companions", []):
                self.player.companions.append(Companion(comp_data["name"], comp_data["effect"]))
            self.player.codex = p.get("codex", [])

            return data.get("floor", 1)
        return 1

    def record_score(self, floor):
        """Persist the current run to the leaderboard file and display it."""
        # Update total run count used for first-run bonuses
        self.total_runs += 1
        try:
            with open(RUN_FILE, "w") as f:
                json.dump({"total_runs": self.total_runs}, f)
        except IOError:
            pass

        records = []
        if os.path.exists(SCORE_FILE):
            try:
                with open(SCORE_FILE) as f:
                    records = json.load(f)
            except (IOError, json.JSONDecodeError):
                records = []

        duration = time.time() - self.run_start if self.run_start else 0
        epitaph = f"Fell on Floor {floor} to '{self.player.cause_of_death or 'Unknown'}'"
        records.append(
            {
                "player_name": self.player.name,
                "score": self.player.get_score(),
                "floor_reached": floor,
                "run_duration": duration,
                "seed": self.seed,
                "epitaph": epitaph,
            }
        )
        records = sorted(records, key=lambda x: x["score"], reverse=True)[:10]
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump(records, f, indent=2)
        except IOError:
            return

        self.view_leaderboard(records)

    def view_leaderboard(self, records=None):
        """Display leaderboard entries stored on disk."""

        if records is None:
            records = []
            if os.path.exists(SCORE_FILE):
                try:
                    with open(SCORE_FILE) as f:
                        records = json.load(f)
                except (IOError, json.JSONDecodeError):
                    records = []

        print(_("-- Leaderboard --"))
        if not records:
            print(_("No scores yet."))
            return
        for r in records:
            print(
                _(
                    f"{r.get('player_name', '?')}: {r.get('score', 0)} "
                    f"(Floor {r.get('floor_reached', '?')}, {r.get('run_duration', 0):.0f}s, Seed {r.get('seed', '?')}) "
                    f"{r.get('epitaph', '')}"
                )
            )

        classes = {
            "1": "Warrior",
            "2": "Mage",
            "3": "Rogue",
            "4": "Cleric",
            "5": "Paladin",
            "6": "Bard",
            "7": "Barbarian",
            "8": "Druid",
            "9": "Ranger",
            "10": "Sorcerer",
            "11": "Monk",
            "12": "Warlock",
            "13": "Necromancer",
            "14": "Shaman",
            "15": "Alchemist",
        }
        names = {v.lower(): k for k, v in classes.items()}
        aliases = {
            "wiz": "mage",
            "sorc": "sorcerer",
            "necro": "necromancer",
            "lock": "warlock",
            "pally": "paladin",
        }

        while True:
            raw = input(_("Class: ")).strip().lower()
            choice = None
            if raw.isdigit() and raw in classes:
                choice = raw
            else:
                key = aliases.get(raw, raw)
                if key in names:
                    choice = names[key]
            if choice is None:
                print(_("Please enter a number (1–15) or a valid class name."))
                continue
            self.player.choose_class(classes[choice])
            break

    def offer_guild(self):
        if self.player.guild:
            return
        print(_("Guilds now accept new members!"))
        print(_("1. Warriors' Guild - Bonus Health"))
        print(_("2. Mages' Guild - Bonus Attack"))
        print(_("3. Rogues' Guild - Faster Skills"))
        print(_("4. Healers' Circle - Extra Vitality"))
        print(_("5. Shadow Brotherhood - Heavy Strikes"))
        print(_("6. Arcane Order - Arcane Mastery"))
        print(_("7. Rangers' Lodge - Balanced Training"))
        print(_("8. Berserkers' Clan - Brutal Strength"))
        choice = input(_("Join which guild? (1-8 or skip): "))
        guilds = {
            "1": "Warriors' Guild",
            "2": "Mages' Guild",
            "3": "Rogues' Guild",
            "4": "Healers' Circle",
            "5": "Shadow Brotherhood",
            "6": "Arcane Order",
            "7": "Rangers' Lodge",
            "8": "Berserkers' Clan",
        }
        if choice in guilds:
            self.player.join_guild(guilds[choice])

    def offer_race(self):
        if self.player.race:
            return
        print(_("New races are available to you!"))
        print(_("1. Human 2. Elf 3. Dwarf 4. Orc 5. Gnome 6. Halfling"))
        print(_("7. Catfolk 8. Lizardfolk 9. Tiefling 10. Aasimar 11. Goblin"))
        print(_("12. Dragonborn 13. Half-Elf 14. Kobold 15. Triton"))
        choice = input(_("Choose your race: "))
        races = {
            "1": "Human",
            "2": "Elf",
            "3": "Dwarf",
            "4": "Orc",
            "5": "Gnome",
            "6": "Halfling",
            "7": "Catfolk",
            "8": "Lizardfolk",
            "9": "Tiefling",
            "10": "Aasimar",
            "11": "Goblin",
            "12": "Dragonborn",
            "13": "Half-Elf",
            "14": "Kobold",
            "15": "Triton",
        }
        race = races.get(choice, "Human")
        self.player.choose_race(race)

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
        map_module.generate_dungeon(self, floor)
        self.generate_quest(floor)

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
                self.player.gold += quest.reward
                self.active_quest = None
        elif isinstance(quest, HuntQuest):
            if quest.is_complete(self):
                print(_("Quest complete!"))
                self.player.gold += quest.reward
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
                self.player.gold += quest.reward
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
            self.trigger_floor_event(floor)

            while self.player.is_alive():
                self.renderer.show_message(
                    _(
                        f"Position: ({self.player.x}, {self.player.y}) - {self.room_names[self.player.y][self.player.x]}"
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
                        "0. Wait 1. Move Left 2. Move Right 3. Move Up 4. Move Down 5. Visit Shop 6. Inventory 7. Quit 8. Show Map 9. View Leaderboard"
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
                    self.stats_logger.end_floor(self)
                    break

        self.renderer.show_message(_("You have died. Game Over!"))
        self.renderer.show_message(
            _(f"Fell on Floor {floor} to '{self.player.cause_of_death or 'Unknown'}'")
        )
        self.renderer.show_message(_(f"Final Score: {self.player.get_score()}"))
        self.record_score(floor)
        self.stats_logger.finalize(self, self.player.cause_of_death or "Unknown")
        if os.path.exists(SAVE_FILE):
            try:
                os.remove(SAVE_FILE)
            except OSError:
                pass

    def handle_input(self, choice: str) -> bool:
        """Handle a menu ``choice`` from the player.

        Returns ``False`` if the player chooses to quit the game, otherwise
        returns ``True`` to continue playing.
        """

        if choice == "0":
            self.player.wait()
        elif choice == "1":
            self.move_player("left")
        elif choice == "2":
            self.move_player("right")
        elif choice == "3":
            self.move_player("up")
        elif choice == "4":
            self.move_player("down")
        elif choice == "5":
            self.shop()
        elif choice == "6":
            self.show_inventory()
        elif choice == "7":
            self.renderer.show_message(_("Thanks for playing!"))
            return False
        elif choice == "8":
            self.render_map()
        elif choice == "9":
            self.view_leaderboard()
        elif config.enable_debug and choice.startswith(":god"):
            self.god_mode(choice)
        elif choice == ":codex":
            self.show_codex()
        else:
            self.renderer.show_message(_(INVALID_KEY_MSG))
        return True

    def god_mode(self, command: str) -> None:
        """Execute debug commands when ``config.enable_debug`` is True."""

        parts = command.split()
        if len(parts) < 2:
            self.renderer.show_message(self.queue_message(_("Usage: :god <spawn|teleport|set>")))
            return

        action = parts[1]
        if action == "spawn" and len(parts) >= 3:
            item_name = " ".join(parts[2:])
            item = Item(item_name, "Debug spawn")
            self.player.inventory.append(item)
            msg = _(f"Spawned {item_name}")
            self.renderer.show_message(self.queue_message(msg))
        elif action == "teleport" and len(parts) >= 3:
            try:
                floor = int(parts[2])
            except ValueError:
                self.renderer.show_message(self.queue_message(_("Invalid floor")))
                return
            self.current_floor = floor
            self.generate_dungeon(floor)
            msg = _(f"Teleported to floor {floor}")
            self.renderer.show_message(self.queue_message(msg))
        elif action == "set" and len(parts) >= 4:
            stat, value = parts[2], parts[3]
            if hasattr(self.player, stat):
                attr = getattr(self.player, stat)
                try:
                    cast_value = type(attr)(value)
                except (TypeError, ValueError):
                    self.renderer.show_message(self.queue_message(_("Invalid value")))
                    return
                setattr(self.player, stat, cast_value)
                msg = _(f"Set {stat} to {cast_value}")
                self.renderer.show_message(self.queue_message(msg))
            else:
                self.renderer.show_message(self.queue_message(_("Unknown stat")))
        else:
            self.renderer.show_message(self.queue_message(_("Invalid god command")))

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

        if self.player.level >= 5 and self.player.health < self.player.max_health:
            self.player.health += 1

        return self.check_floor_completion(floor)

    def check_floor_completion(self, floor: int):
        """Determine if the current floor has been completed.

        Returns ``(new_floor, status)`` similar to :meth:`process_turn`.
        """

        if (
            self.player.x == self.exit_coords[0]
            and self.player.y == self.exit_coords[1]
            and self.player.has_item("Key")
        ):
            self.renderer.show_message(_("You reach the Sealed Gate."))
            proceed = input(_("Would you like to descend to the next floor? (y/n): ")).lower()
            if proceed == "y":
                floor += 1
                # Reset temporary floor buffs
                self.player.temp_strength = 0
                self.player.temp_intelligence = 0
                self.save_game(floor)
                return floor, False
            self.renderer.show_message(_("You chose to exit the dungeon."))
            self.renderer.show_message(_(f"Final Score: {self.player.get_score()}"))
            self.record_score(floor)
            if os.path.exists(SAVE_FILE):
                try:
                    os.remove(SAVE_FILE)
                except OSError:
                    pass
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
            print(_(f"Correct! You receive {reward} gold."))
            self.player.gold += reward
        else:
            print(_("Incorrect! The sage vanishes in disappointment."))

    def trigger_random_event(self, floor):
        """Randomly select and trigger an event for ``floor``."""
        cfg = self.floor_configs.get(floor, {})
        events = cfg.get("events")
        if events:
            weights = []
            for ev in events:
                name = ev.__name__.replace("Event", "").lower()
                weight = cfg.get(f"{name}_rate", 1.0)
                weights.append(weight)
            event_cls = random.choices(events, weights=weights, k=1)[0]
            event = event_cls()
            event.trigger(self)

    # Floor-specific events keep gameplay varied without hardcoding logic in
    # play_game. Additional floors can be added here easily.
    def trigger_floor_event(self, floor):
        events = {
            1: self._floor_one_event,
            2: self._floor_two_event,
            3: self._floor_three_event,
            5: self._floor_five_event,
            8: self._floor_eight_event,
            12: self._floor_twelve_event,
            15: self._floor_fifteen_event,
        }
        if floor in events:
            events[floor]()

    def _floor_one_event(self):
        print(_("The crowd roars as you step into the arena for the first time."))
        self.offer_class()
        event_cls = random.choice([FountainEvent, CacheEvent])
        event_cls().trigger(self)

    def _floor_two_event(self):
        self.offer_guild()
        options = [CacheEvent, TrapEvent, LoreNoteEvent]
        for __ in range(random.randint(1, 2)):
            random.choice(options)().trigger(self)

    def _floor_three_event(self):
        self.offer_race()
        options = [ShrineEvent, MiniQuestHookEvent, HazardEvent]
        for __ in range(2):
            random.choice(options)().trigger(self)

    def _floor_five_event(self):
        print(_("A mysterious merchant sets up shop, selling exotic wares."))

    def _floor_eight_event(self):
        print(_("You stumble upon a radiant shrine, filling you with determination."))
        self.grant_inspiration()

    def _floor_twelve_event(self):
        print(_("An elusive merchant appears, offering rare goods."))
        self.shop()

    def _floor_fifteen_event(self):
        print(_("A robed sage blocks your path, offering a riddle challenge."))
        self.riddle_challenge()
