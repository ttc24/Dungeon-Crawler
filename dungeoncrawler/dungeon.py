import json
import os
import random
from functools import lru_cache
from pathlib import Path

from .constants import ANNOUNCER_LINES, RIDDLES, SAVE_FILE, SCORE_FILE
from .entities import Companion, Enemy, Player
from .items import Item, Weapon
from .plugins import apply_enemy_plugins, apply_item_plugins
from . import combat as combat_module
from . import map as map_module
from . import shop as shop_module

# ---------------------------------------------------------------------------
# Data loading utilities
# ---------------------------------------------------------------------------
# ``data/enemies.json`` schema:
# {
#   "EnemyName": {
#     "stats": [hp_min, hp_max, atk_min, atk_max, defense],
#     "ability": "optional"
#   },
#   ...
# }
#
# ``data/bosses.json`` schema:
# {
#   "BossName": {
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
#     ]
#   },
#   ...
# }

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
    """Load enemy stats and abilities from ``enemies.json``."""
    path = DATA_DIR / "enemies.json"
    with open(path) as f:
        data = json.load(f)
    stats = {name: tuple(v["stats"]) for name, v in data.items()}
    abilities = {name: v.get("ability") for name, v in data.items() if v.get("ability")}
    return stats, abilities


@lru_cache(maxsize=None)
def load_bosses():
    """Load boss stats and loot tables from ``bosses.json``."""
    path = DATA_DIR / "bosses.json"
    with open(path) as f:
        data = json.load(f)
    stats = {}
    loot = {}
    for name, cfg in data.items():
        hp, atk, dfs, gold = cfg["stats"]
        stats[name] = (hp, atk, dfs, gold, cfg.get("ability"))
        if "loot" in cfg:
            loot[name] = [Weapon(**item) for item in cfg["loot"]]
    return stats, loot


ENEMY_STATS, ENEMY_ABILITIES = load_enemies()
BOSS_STATS, BOSS_LOOT = load_bosses()
apply_enemy_plugins(ENEMY_STATS, ENEMY_ABILITIES)
# Floor specific configuration
FLOOR_CONFIGS = {
    1: {
        "size": (8, 8),
        "enemies": ["Goblin", "Skeleton", "Bandit"],
        "bosses": ["Bone Tyrant"],
        "places": {
            "Trap": 2,
            "Treasure": 2,
            "Enchantment": 1,
            "Sanctuary": 1,
            "Blacksmith": 1,
        },
    },
    2: {
        "size": (9, 9),
        "enemies": ["Orc", "Cultist", "Ghoul", "Bandit"],
        "bosses": ["Inferno Golem", "Frost Warden"],
        "places": {
            "Trap": 3,
            "Treasure": 3,
            "Enchantment": 1,
            "Sanctuary": 1,
            "Blacksmith": 1,
        },
    },
    3: {
        "size": (10, 10),
        "enemies": ["Vampire", "Warlock", "Wraith", "Werewolf"],
        "bosses": ["Shadow Reaver", "Doom Bringer"],
        "places": {
            "Trap": 3,
            "Treasure": 4,
            "Enchantment": 2,
            "Sanctuary": 2,
            "Blacksmith": 1,
        },
    },
    4: {
        "size": (11, 11),
        "enemies": ["Basilisk", "Gargoyle", "Troll", "Lich"],
        "bosses": ["Void Serpent", "Ember Lord", "Glacier Fiend"],
        "places": {
            "Trap": 4,
            "Treasure": 4,
            "Enchantment": 2,
            "Sanctuary": 2,
            "Blacksmith": 1,
        },
    },
    5: {
        "size": (12, 12),
        "enemies": ["Phoenix", "Hydra", "Revenant", "Beholder"],
        "bosses": ["Grave Monarch", "Storm Reaper"],
        "places": {
            "Trap": 4,
            "Treasure": 5,
            "Enchantment": 2,
            "Sanctuary": 2,
            "Blacksmith": 1,
        },
    },
    6: {
        "size": (13, 13),
        "enemies": ["Minotaur", "Demon", "Harpy", "Shade"],
        "bosses": ["Bone Tyrant", "Inferno Golem"],
        "places": {
            "Trap": 5,
            "Treasure": 5,
            "Enchantment": 2,
            "Sanctuary": 2,
            "Blacksmith": 1,
        },
    },
    7: {
        "size": (14, 14),
        "enemies": ["Giant Spider", "Slime King", "Zombie", "Gargoyle"],
        "bosses": ["Frost Warden", "Shadow Reaver"],
        "places": {
            "Trap": 5,
            "Treasure": 6,
            "Enchantment": 2,
            "Sanctuary": 2,
            "Blacksmith": 1,
        },
    },
    8: {
        "size": (15, 15),
        "enemies": ["Dark Knight", "Cyclops", "Basilisk", "Werewolf"],
        "bosses": ["Doom Bringer", "Void Serpent"],
        "places": {
            "Trap": 5,
            "Treasure": 6,
            "Enchantment": 3,
            "Sanctuary": 2,
            "Blacksmith": 1,
        },
    },
    9: {
        "size": (15, 15),
        "enemies": ["Hydra", "Beholder", "Revenant", "Warlock"],
        "bosses": ["Ember Lord", "Glacier Fiend"],
        "places": {
            "Trap": 6,
            "Treasure": 6,
            "Enchantment": 3,
            "Sanctuary": 2,
            "Blacksmith": 1,
        },
    },
    10: {
        "size": (15, 15),
        "enemies": ["Phoenix", "Dark Knight", "Cyclops", "Minotaur"],
        "bosses": ["Grave Monarch", "Storm Reaper"],
        "places": {
            "Trap": 6,
            "Treasure": 7,
            "Enchantment": 3,
            "Sanctuary": 3,
            "Blacksmith": 1,
        },
    },
    11: {
        "size": (15, 15),
        "enemies": ["Astral Dragon", "Demon", "Harpy", "Shade"],
        "bosses": ["Bone Tyrant", "Inferno Golem", "Frost Warden"],
        "places": {
            "Trap": 7,
            "Treasure": 7,
            "Enchantment": 3,
            "Sanctuary": 3,
            "Blacksmith": 1,
        },
    },
    12: {
        "size": (15, 15),
        "enemies": ["Giant Spider", "Slime King", "Zombie", "Warlock"],
        "bosses": ["Shadow Reaver", "Doom Bringer", "Void Serpent"],
        "places": {
            "Trap": 7,
            "Treasure": 8,
            "Enchantment": 4,
            "Sanctuary": 3,
            "Blacksmith": 1,
        },
    },
    13: {
        "size": (15, 15),
        "enemies": ["Basilisk", "Gargoyle", "Troll", "Lich"],
        "bosses": ["Ember Lord", "Glacier Fiend", "Grave Monarch"],
        "places": {
            "Trap": 8,
            "Treasure": 8,
            "Enchantment": 4,
            "Sanctuary": 3,
            "Blacksmith": 1,
        },
    },
    14: {
        "size": (15, 15),
        "enemies": ["Hydra", "Beholder", "Revenant", "Dark Knight"],
        "bosses": ["Storm Reaper"],
        "places": {
            "Trap": 8,
            "Treasure": 9,
            "Enchantment": 4,
            "Sanctuary": 3,
            "Blacksmith": 1,
        },
    },
    15: {
        "size": (15, 15),
        "enemies": ["Cyclops", "Astral Dragon", "Phoenix", "Minotaur"],
        "bosses": ["Doom Bringer", "Void Serpent"],
        "places": {
            "Trap": 9,
            "Treasure": 9,
            "Enchantment": 5,
            "Sanctuary": 3,
            "Blacksmith": 1,
        },
    },
    16: {
        "size": (15, 15),
        "enemies": ["Demon", "Harpy", "Shade", "Giant Spider"],
        "bosses": ["Ember Lord", "Glacier Fiend"],
        "places": {
            "Trap": 9,
            "Treasure": 10,
            "Enchantment": 5,
            "Sanctuary": 3,
            "Blacksmith": 1,
        },
    },
    17: {
        "size": (15, 15),
        "enemies": ["Slime King", "Zombie", "Gargoyle", "Warlock"],
        "bosses": ["Grave Monarch", "Storm Reaper"],
        "places": {
            "Trap": 9,
            "Treasure": 10,
            "Enchantment": 5,
            "Sanctuary": 4,
            "Blacksmith": 1,
        },
    },
    18: {
        "size": (15, 15),
        "enemies": ["Hydra", "Beholder", "Astral Dragon", "Dark Knight"],
        "bosses": ["Bone Tyrant", "Doom Bringer", "Void Serpent"],
        "places": {
            "Trap": 10,
            "Treasure": 10,
            "Enchantment": 6,
            "Sanctuary": 4,
            "Blacksmith": 1,
        },
    },
}


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
        self.rooms = [[None for _ in range(width)] for _ in range(height)]
        self.room_names = [
            [self.generate_room_name() for _ in range(width)] for _ in range(height)
        ]
        self.visited_rooms = set()
        self.player = None
        self.exit_coords = None
        self.shop_items = [
            Item("Health Potion", "Restores 20 health"),
            Weapon("Sword", "A sharp sword", 10, 15, 40),
            Weapon("Axe", "A heavy axe", 12, 18, 65),
            Weapon("Dagger", "A quick dagger", 8, 12, 35),
            Weapon("Warhammer", "Crushes armor and bone", 14, 22, 85),
            Weapon("Rapier", "A slender, piercing blade", 9, 17, 50),
            Weapon("Flame Blade", "Glows with searing heat", 13, 20, 95),
            Weapon("Crossbow", "Ranged attack with bolts", 11, 19, 60),
        ]
        self.rare_loot = [
            Weapon("Elven Longbow", "Bow of unmatched accuracy.", 15, 25, 0),
            Item("Blessed Charm", "Said to bring good fortune."),
            Weapon("Dwarven Waraxe", "Forged in the deep halls.", 12, 20, 0),
            Item("Shadow Cloak", "Grants an air of mystery"),
        ]
        apply_item_plugins(self.shop_items)
        self.riddles = RIDDLES
        self.enemy_stats = ENEMY_STATS
        self.enemy_abilities = ENEMY_ABILITIES
        self.boss_stats = BOSS_STATS
        self.boss_loot = BOSS_LOOT
        self.floor_configs = FLOOR_CONFIGS

    def announce(self, msg):
        print(f"[Announcer] {random.choice(ANNOUNCER_LINES)} {msg}")

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
            "player": {
                "name": self.player.name,
                "level": self.player.level,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "attack_power": self.player.attack_power,
                "xp": self.player.xp,
                "gold": self.player.gold,
                "class": self.player.class_type,
                "cooldown": self.player.skill_cooldown,
                "guild": self.player.guild,
                "race": self.player.race,
                "inventory": [serialize_item(it) for it in self.player.inventory],
                "weapon": serialize_item(self.player.weapon),
                "companions": [
                    {"name": c.name, "effect": c.effect} for c in self.player.companions
                ],
            },
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE) as f:
                data = json.load(f)
            self.player = Player(
                data["player"]["name"], data["player"].get("class", "Novice")
            )
            p = data["player"]
            self.player.level = p["level"]
            self.player.health = p["health"]
            self.player.max_health = p["max_health"]
            self.player.attack_power = p["attack_power"]
            self.player.xp = p["xp"]
            self.player.gold = p["gold"]
            self.player.skill_cooldown = p.get("cooldown", 0)
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
                self.player.companions.append(
                    Companion(comp_data["name"], comp_data["effect"])
                )

            return data.get("floor", 1)
        return 1

    def record_score(self, floor):
        records = []
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE) as f:
                records = json.load(f)
        records.append(
            {"name": self.player.name, "score": self.player.get_score(), "floor": floor}
        )
        records = sorted(records, key=lambda x: x["score"], reverse=True)[:10]
        with open(SCORE_FILE, "w") as f:
            json.dump(records, f, indent=2)
        print("-- Leaderboard --")
        for r in records:
            print(f"{r['name']}: {r['score']} (Floor {r.get('floor', '?')})")

    def offer_class(self):
        if self.player.class_type != "Novice":
            return
        print("It's time to choose your class!")
        print("1. Warrior 2. Mage 3. Rogue 4. Cleric 5. Paladin 6. Bard")
        print("7. Barbarian 8. Druid 9. Ranger 10. Sorcerer 11. Monk")
        print("12. Warlock 13. Necromancer 14. Shaman 15. Alchemist")
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
        choice = ""
        while choice not in classes:
            choice = input("Class: ")
            if choice not in classes:
                print("Invalid choice. Please try again.")
        self.player.choose_class(classes[choice])

    def offer_guild(self):
        if self.player.guild:
            return
        print("Guilds now accept new members!")
        print("1. Warriors' Guild - Bonus Health")
        print("2. Mages' Guild - Bonus Attack")
        print("3. Rogues' Guild - Faster Skills")
        print("4. Healers' Circle - Extra Vitality")
        print("5. Shadow Brotherhood - Heavy Strikes")
        print("6. Arcane Order - Arcane Mastery")
        print("7. Rangers' Lodge - Balanced Training")
        print("8. Berserkers' Clan - Brutal Strength")
        choice = input("Join which guild? (1-8 or skip): ")
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
        print("New races are available to you!")
        print("1. Human 2. Elf 3. Dwarf 4. Orc 5. Gnome 6. Halfling")
        print("7. Catfolk 8. Lizardfolk 9. Tiefling 10. Aasimar 11. Goblin")
        print("12. Dragonborn 13. Half-Elf 14. Kobold 15. Triton")
        choice = input("Choose your race: ")
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
        lore = {
            "Treasure": (
                "Glittering Vault",
                "The air shimmers with unseen magic. Ancient riches may lie within.",
            ),
            "Trap": (
                "Booby-Trapped Passage",
                "This corridor is riddled with pressure plates and crumbled bones.",
            ),
            "Enemy": (
                "Cursed Hall",
                "The shadows shift... something watches from the dark.",
            ),
            "Exit": (
                "Sealed Gate",
                "Massive stone doors sealed by arcane runes. It might be the only way out.",
            ),
            "Key": (
                "Hidden Niche",
                "A hollow carved into the wall, forgotten by time. Something valuable glints inside.",
            ),
            "Sanctuary": (
                "Sacred Sanctuary",
                "A calm aura fills this room, soothing your wounds.",
            ),
            "Empty": (
                "Silent Chamber",
                "Dust covers everything. It appears long abandoned.",
            ),
            "default": (None, None),
        }

        if room_type in lore:
            return lore[room_type][0]

        return f"{random.choice(ROOM_NAME_ADJECTIVES)} {random.choice(ROOM_NAME_NOUNS)}"

    def generate_dungeon(self, floor=1):
        map_module.generate_dungeon(self, floor)

    def play_game(self) -> None:
        """Run the main game loop until the player quits or dies."""

        if self.player is None:
            floor = self.load_game()
            if self.player:
                cont = input("Continue your last adventure? (y/n): ")
                if cont.lower() != "y":
                    self.player = None
                    floor = 1
        else:
            floor = 1
        if self.player is None:
            raise ValueError("Player must be created before starting the game.")
        print("Welcome to Dungeon Crawler!")
        while self.player.is_alive() and floor <= 18:
            print(f"===== Entering Floor {floor} =====")
            self.generate_dungeon(floor)
            self.trigger_floor_event(floor)

            while self.player.is_alive():
                print(
                    f"Position: ({self.player.x}, {self.player.y}) - {self.room_names[self.player.y][self.player.x]}"
                )
                print(
                    f"Health: {self.player.health} | XP: {self.player.xp} | Gold: {self.player.gold} | Level: {self.player.level} | Floor: {floor} | Skill CD: {self.player.skill_cooldown}"
                )
                if self.player.guild:
                    print(f"Guild: {self.player.guild}")
                if self.player.race:
                    print(f"Race: {self.player.race}")
                print(
                    "1. Move Left 2. Move Right 3. Move Up 4. Move Down 5. Visit Shop 6. Inventory 7. Quit 8. Show Map"
                )
                choice = input("Action: ")

                if choice == "1":
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
                    print("Thanks for playing!")
                    return
                elif choice == "8":
                    self.render_map()
                else:
                    print("Invalid choice!")

                if (
                    self.player.level >= 5
                    and self.player.health < self.player.max_health
                ):
                    self.player.health += 1

                if (
                    self.player.x == self.exit_coords[0]
                    and self.player.y == self.exit_coords[1]
                    and self.player.has_item("Key")
                ):
                    print("You reach the Sealed Gate.")
                    proceed = input(
                        "Would you like to descend to the next floor? (y/n): "
                    ).lower()
                    if proceed == "y":
                        floor += 1
                        self.save_game(floor)
                        break
                    else:
                        print("You chose to exit the dungeon.")
                        print(f"Final Score: {self.player.get_score()}")
                        self.record_score(floor)
                        if os.path.exists(SAVE_FILE):
                            os.remove(SAVE_FILE)
                        return

        print("You have died. Game Over!")
        print(f"Final Score: {self.player.get_score()}")
        self.record_score(floor)
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

    def move_player(self, direction):
        map_module.move_player(self, direction)

    def render_map(self):
        map_module.render_map(self)

    def handle_room(self, x, y):
        map_module.handle_room(self, x, y)

    def battle(self, enemy):
        combat_module.battle(self, enemy)

    def audience_gift(self):
        if random.random() < 0.1:
            print("A package falls from above! It's a gift from the audience.")
            if random.random() < 0.5:
                item = Item("Health Potion", "Restores 20 health")
                self.player.collect_item(item)
                print(f"You received a {item.name}.")
                self.announce(f"{self.player.name} gains a helpful item!")
            else:
                damage = random.randint(5, 15)
                self.player.take_damage(damage)
                print(f"Uh-oh! It explodes and deals {damage} damage.")
                self.announce("The crowd loves a good prank!")

    def grant_inspiration(self, turns=3):
        """Give the player a temporary inspire buff."""
        self.player.status_effects["inspire"] = turns

    def shop(self):
        shop_module.shop(self)

    def get_sale_price(self, item):
        return shop_module.get_sale_price(item)

    def sell_items(self):
        shop_module.sell_items(self)

    def show_inventory(self):
        shop_module.show_inventory(self)

    def riddle_challenge(self):
        """Present the player with a riddle for a potential reward."""
        riddle, answer = random.choice(self.riddles)
        print("A sage poses a riddle:\n" + riddle)
        response = input("Answer: ").strip().lower()
        if response == answer:
            reward = 50
            print(f"Correct! You receive {reward} gold.")
            self.player.gold += reward
        else:
            print("Incorrect! The sage vanishes in disappointment.")

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
        print("The crowd roars as you step into the arena for the first time.")
        self.offer_class()

    def _floor_two_event(self):
        self.offer_guild()

    def _floor_three_event(self):
        self.offer_race()

    def _floor_five_event(self):
        print("A mysterious merchant sets up shop, selling exotic wares.")

    def _floor_eight_event(self):
        print("You stumble upon a radiant shrine, filling you with determination.")
        self.grant_inspiration()

    def _floor_twelve_event(self):
        print("An elusive merchant appears, offering rare goods.")
        self.shop()

    def _floor_fifteen_event(self):
        print("A robed sage blocks your path, offering a riddle challenge.")
        self.riddle_challenge()
