import json
import os
import random
from pathlib import Path

from .constants import ANNOUNCER_LINES, RIDDLES, SAVE_FILE, SCORE_FILE
from .entities import Companion, Enemy, Player
from .items import Item, Weapon

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


def load_enemies():
    """Load enemy stats and abilities from ``enemies.json``."""
    path = DATA_DIR / "enemies.json"
    with open(path) as f:
        data = json.load(f)
    stats = {name: tuple(v["stats"]) for name, v in data.items()}
    abilities = {name: v.get("ability") for name, v in data.items() if v.get("ability")}
    return stats, abilities


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
                "Massive stone doors sealed by arcane runes. It might be the only way out.",  # noqa: E501
            ),
            "Key": (
                "Hidden Niche",
                "A hollow carved into the wall, forgotten by time. Something valuable glints inside.",  # noqa: E501
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

        adjectives = [
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
        nouns = [
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
        return f"{random.choice(adjectives)} {random.choice(nouns)}"

    def generate_dungeon(self, floor=1):
        cfg = FLOOR_CONFIGS.get(floor)
        if cfg is None:
            raise ValueError(f"Floor {floor} is not configured")
        size = cfg.get("size", (min(15, 8 + floor), min(15, 8 + floor)))
        self.width, self.height = size
        self.rooms = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.room_names = [
            [self.generate_room_name() for _ in range(self.width)]
            for _ in range(self.height)
        ]
        visited = set()
        path = []
        x, y = self.width // 2, self.height // 2
        start = (x, y)
        visited.add(start)
        path.append(start)

        while len(visited) < (self.width * self.height) // 2:
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            nx, ny = x + direction[0], y + direction[1]
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    path.append((nx, ny))
                x, y = nx, ny

        for x, y in visited:
            self.rooms[y][x] = "Empty"

        if self.player is None:
            raise ValueError("Player must be created before generating the dungeon.")
        self.rooms[start[1]][start[0]] = self.player
        self.player.x, self.player.y = start
        self.visited_rooms.add(start)

        visited.remove(start)
        visited = list(visited)
        random.shuffle(visited)

        def place(obj):
            if visited:
                x, y = visited.pop()
                self.rooms[y][x] = obj
                return (x, y)

        self.exit_coords = place("Exit")
        place(Item("Key", "Opens the dungeon exit"))

        enemy_names = cfg["enemies"]
        early_game_bonus = 5 if floor <= 3 else 0
        for _ in range(5 + floor):
            name = random.choice(enemy_names)
            hp_min, hp_max, atk_min, atk_max, defense = ENEMY_STATS[name]

            hp_scale = 1 if floor <= 3 else 2
            atk_scale = 1 if floor <= 3 else 2

            defense = max(1, defense + floor // 3)

            health = random.randint(
                hp_min + floor * hp_scale, hp_max + floor * hp_scale
            )
            attack = random.randint(
                atk_min + floor * atk_scale,
                atk_max + floor * atk_scale,
            )
            gold = random.randint(15 + early_game_bonus + floor, 30 + floor * 2)

            ability = ENEMY_ABILITIES.get(name)
            enemy = Enemy(name, health, attack, defense, gold, ability)
            enemy.xp = max(5, (health + attack + defense) // 15)

            place(enemy)

        boss_names = cfg["bosses"]
        name = random.choice(boss_names)
        hp, atk, dfs, gold, ability = BOSS_STATS[name]
        print(f"A powerful boss guards this floor! The {name} lurks nearby...")
        boss = Enemy(
            name,
            hp + floor * 10,
            atk + floor,
            dfs + floor // 2,
            gold + floor * 5,
            ability=ability,
        )
        place(boss)
        boss_drop = BOSS_LOOT.get(name, [])
        if boss_drop and random.random() < 0.5:
            loot = random.choice(boss_drop)
            print(f"✨ The boss dropped a unique weapon: {loot.name}!")
            place(loot)

        place(Item("Key", "A magical key dropped by the boss"))
        companion_options = [
            Companion("Battle Priest", "heal"),
            Companion("Hired Blade", "attack"),
        ]
        place(random.choice(companion_options))
        default_places = {
            "Trap": 3,
            "Treasure": 3,
            "Enchantment": 2,
            "Sanctuary": 2,
            "Blacksmith": 1,
        }
        place_counts = default_places.copy()
        place_counts.update(cfg.get("places", {}))
        for pname, count in place_counts.items():
            for _ in range(count):
                place(pname)
        # Key is now tied to boss drop; don't place it separately

    def play_game(self):
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
                    f"Position: ({self.player.x}, {self.player.y}) - {self.room_names[self.player.y][self.player.x]}"  # noqa: E501
                )
                print(
                    f"Health: {self.player.health} | XP: {self.player.xp} | Gold: {self.player.gold} | Level: {self.player.level} | Floor: {floor} | Skill CD: {self.player.skill_cooldown}"  # noqa: E501
                )
                if self.player.guild:
                    print(f"Guild: {self.player.guild}")
                if self.player.race:
                    print(f"Race: {self.player.race}")
                print(
                    "1. Move Left 2. Move Right 3. Move Up 4. Move Down 5. Visit Shop 6. Inventory 7. Quit 8. Show Map"  # noqa: E501
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
        dx, dy = {"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}.get(
            direction, (0, 0)
        )
        x, y = self.player.x + dx, self.player.y + dy
        if (
            0 <= x < self.width
            and 0 <= y < self.height
            and self.rooms[y][x] is not None
        ):
            self.handle_room(x, y)
        else:
            print("You can't move that way.")

    def render_map(self):
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                pos = (x, y)
                if pos == (self.player.x, self.player.y):
                    row += "@"
                elif pos in self.visited_rooms or pos == self.exit_coords:
                    row += "."
                else:
                    row += "#"
            print(row)

    def handle_room(self, x, y):
        room = self.rooms[y][x]
        name = self.room_names[y][x]
        lore = {
            "Glittering Vault": "The air shimmers with unseen magic. Ancient riches may lie within.",  # noqa: E501
            "Booby-Trapped Passage": "This corridor is riddled with pressure plates and crumbled bones.",  # noqa: E501
            "Cursed Hall": "The shadows shift... something watches from the dark.",
            "Sealed Gate": "Massive stone doors sealed by arcane runes. It might be the only way out.",  # noqa: E501
            "Hidden Niche": "A hollow carved into the wall, forgotten by time. Something valuable glints inside.",  # noqa: E501
            "Silent Chamber": "Dust covers everything. It appears long abandoned.",
            "Sacred Sanctuary": "A peaceful place that heals weary adventurers.",
        }
        if name in lore:
            print(f"{lore[name]}")

        if isinstance(room, Enemy):
            self.battle(room)
            if not room.is_alive():
                self.rooms[y][x] = None
        elif isinstance(room, Companion):
            print(f"You meet {room.name}. {room.description}")
            recruit = input("Recruit this companion? (y/n): ")
            if recruit.lower() == "y":
                self.player.companions.append(room)
                if room.effect == "attack":
                    self.player.attack_power += 2
                elif room.effect == "heal":
                    self.player.max_health += 5
                    self.player.health += 5
                self.announce(f"{self.player.name} gains a companion!")
            self.rooms[y][x] = None
        elif isinstance(room, Item):
            print(f"You found a {room.name}!")
            self.player.collect_item(room)
            self.announce(f"{self.player.name} obtained {room.name}!")
            self.rooms[y][x] = None
            if room.name == "Key":
                self.room_names[y][x] = "Hidden Niche"
        elif room == "Treasure":
            gold = random.randint(20, 50)
            self.player.gold += gold
            print(f"You found a treasure chest with {gold} gold!")
            if random.random() < 0.3:
                loot = random.choice(self.rare_loot)
                print(f"Inside you also discover {loot.name}!")
                self.player.collect_item(loot)
                self.announce(f"{self.player.name} picks up {loot.name}!")
            self.rooms[y][x] = None
            self.room_names[y][x] = "Glittering Vault"
        elif room == "Enchantment":
            print("You enter a glowing chamber with ancient runes etched in the stone.")
            if self.player.weapon:
                print(f"Your current weapon is: {self.player.weapon.name}")
                print("You may enchant it with a status effect for 30 gold.")
                print("1. Poison  2. Burn  3. Freeze  4. Cancel")
                choice = input("Choose enchantment: ")
                if self.player.weapon.effect:
                    print(
                        "Your weapon is already enchanted! You can't add another enchantment."  # noqa: E501
                    )
                elif self.player.gold >= 30 and choice in ["1", "2", "3"]:
                    effect = {"1": "poison", "2": "burn", "3": "freeze"}[choice]
                    self.player.weapon.description += f" (Enchanted: {effect})"
                    self.player.weapon.effect = effect
                    self.player.gold -= 30
                    print(f"Your weapon is now enchanted with {effect}!")
                elif choice == "4":
                    print("You leave the enchantment chamber untouched.")
                else:
                    print("Not enough gold or invalid choice.")
            else:
                print("You need a weapon to enchant.")
            self.rooms[y][x] = None
            self.room_names[y][x] = "Enchantment Chamber"
        elif room == "Blacksmith":
            print("You meet a grizzled blacksmith hammering at a forge.")
            if self.player.weapon:
                print(
                    f"Your weapon: {self.player.weapon.name} ({self.player.weapon.min_damage}-{self.player.weapon.max_damage})"  # noqa: E501
                )
                print(
                    "Would you like to upgrade your weapon for 50 gold? +3 min/max damage"  # noqa: E501
                )
                confirm = input("Upgrade? (y/n): ")
                if confirm.lower() == "y" and self.player.gold >= 50:
                    self.player.weapon.min_damage += 3
                    self.player.weapon.max_damage += 3
                    self.player.gold -= 50
                    print("Your weapon has been reforged and is stronger!")
                elif self.player.gold < 50:
                    print("You don't have enough gold.")
                else:
                    print("Maybe next time.")
            else:
                print(
                    "The blacksmith scoffs. 'No weapon? Come back when you have something worth forging.'"  # noqa: E501
                )
            self.rooms[y][x] = None
            self.room_names[y][x] = "Blacksmith Forge"

        elif room == "Sanctuary":
            self.player.health = self.player.max_health
            print("A soothing warmth envelops you. Your wounds are fully healed.")
            self.rooms[y][x] = None
            self.room_names[y][x] = "Sacred Sanctuary"

        elif room == "Trap":
            riddle = random.choice(RIDDLES)
            print("A trap springs! Solve this riddle to escape unharmed:")
            print(riddle["question"])
            response = input("Answer: ").strip().lower()
            if response == riddle["answer"].lower():
                print("The mechanism clicks harmlessly. You solved it!")
                self.announce("Brilliant puzzle solving!")
            else:
                damage = random.randint(10, 30)
                self.player.take_damage(damage)
                print(f"Wrong answer! You take {damage} damage.")
            self.rooms[y][x] = None
            self.room_names[y][x] = "Booby-Trapped Passage"
        elif room == "Exit":
            self.room_names[y][x] = "Sealed Gate"
            if self.player.has_item("Key"):
                print("🎉 You unlocked the exit and escaped the dungeon!")
                print(f"Final Score: {self.player.get_score()}")
                exit()
            else:
                print("The exit is locked. You need a key!")

        self.rooms[self.player.y][self.player.x] = None
        self.player.x, self.player.y = x, y
        self.rooms[y][x] = self.player
        self.visited_rooms.add((x, y))
        self.audience_gift()

    def battle(self, enemy):
        print(
            f"You encountered a {enemy.name}! {enemy.ability.capitalize() if enemy.ability else ''} Boss incoming!"  # noqa: E501
        )
        self.announce(f"{self.player.name} engages {enemy.name}!")
        while self.player.is_alive() and enemy.is_alive():
            self.player.apply_status_effects()
            for companion in getattr(self.player, "companions", []):
                companion.assist(self.player, enemy)
            if not enemy.is_alive():
                break
            if "freeze" in self.player.status_effects:
                print("\u2744\ufe0f You are frozen and skip this turn!")
                self.player.status_effects["freeze"] -= 1
                if self.player.status_effects["freeze"] <= 0:
                    del self.player.status_effects["freeze"]
                if enemy.is_alive():
                    enemy.attack(self.player)
                continue

            print(f"Player Health: {self.player.health}")
            print(f"Enemy Health: {enemy.health}")
            print("1. Attack\n2. Defend\n3. Use Health Potion\n4. Use Skill")
            choice = input("Choose action: ")
            if choice == "1":
                self.player.attack(enemy)
                self.announce("A fierce attack lands!")
                if enemy.is_alive():
                    skip = enemy.apply_status_effects()
                    if enemy.is_alive() and not skip:
                        enemy.attack(self.player)
            elif choice == "2":
                self.player.defend(enemy)
                if enemy.is_alive():
                    skip = enemy.apply_status_effects()
                    if enemy.is_alive() and not skip:
                        enemy.attack(self.player)
            elif choice == "3":
                self.player.use_health_potion()
                if enemy.is_alive():
                    skip = enemy.apply_status_effects()
                    if enemy.is_alive() and not skip:
                        enemy.attack(self.player)
            elif choice == "4":
                self.player.use_skill(enemy)
                self.announce("Special skill unleashed!")
                if enemy.is_alive():
                    skip = enemy.apply_status_effects()
                    if enemy.is_alive() and not skip:
                        enemy.attack(self.player)
            else:
                print("Invalid choice!")
            self.player.decrement_cooldowns()

        if not enemy.is_alive():
            self.announce(f"{enemy.name} has been defeated!")
            # Award boss-specific loot directly to the player
            if enemy.name in BOSS_LOOT:
                loot = random.choice(BOSS_LOOT[enemy.name])
                self.player.collect_item(loot)
                print(f"The {enemy.name} dropped {loot.name}!")
                self.announce(f"{self.player.name} obtains {loot.name}!")

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
        print("Welcome to the Shop!")
        print(f"Gold: {self.player.gold}")
        for i, item in enumerate(self.shop_items, 1):
            price = item.price if isinstance(item, Weapon) else 10
            print(f"{i}. {item.name} - {price} Gold")
        sell_option = len(self.shop_items) + 1
        exit_option = sell_option + 1
        print(f"{sell_option}. Sell Items")
        print(f"{exit_option}. Exit")

        choice = input("Choose an option:")
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(self.shop_items):
                item = self.shop_items[choice - 1]
                price = item.price if isinstance(item, Weapon) else 10
                if self.player.gold >= price:
                    self.player.collect_item(item)
                    self.player.gold -= price
                    print(f"You bought {item.name}.")
                else:
                    print("Not enough gold.")
            elif choice == sell_option:
                self.sell_items()
            elif choice == exit_option:
                print("Leaving the shop.")
            else:
                print("Invalid choice.")
        else:
            print("Invalid input.")

    def get_sale_price(self, item):
        if isinstance(item, Weapon):
            price = getattr(item, "price", 0)
            if price > 0:
                return price // 2
            return None
        if isinstance(item, Item):
            return 5
        return None

    def sell_items(self):
        if not self.player.inventory:
            print("You have nothing to sell.")
            return

        print("Your Items:")
        for i, item in enumerate(self.player.inventory, 1):
            sale_price = self.get_sale_price(item)
            if sale_price is None:
                print(f"{i}. {item.name} - Cannot sell")
            else:
                print(f"{i}. {item.name} - {sale_price} Gold")
        print(f"{len(self.player.inventory)+1}. Back")

        choice = input("Sell what?")
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(self.player.inventory):
                item = self.player.inventory[choice - 1]
                sale_price = self.get_sale_price(item)
                if sale_price is None:
                    print("You can't sell that item.")
                    return
                confirm = input(f"Sell {item.name} for {sale_price} gold? (y/n) ")
                if confirm.lower() == "y":
                    self.player.inventory.pop(choice - 1)
                    self.player.gold += sale_price
                    print(f"You sold {item.name}.")
            elif choice == len(self.player.inventory) + 1:
                return
            else:
                print("Invalid choice.")
        else:
            print("Invalid input.")

    def show_inventory(self):
        if not self.player.inventory:
            print("Your inventory is empty.")
            return

        print("Your Inventory:")
        for i, item in enumerate(self.player.inventory, 1):
            equipped = " (Equipped)" if item == self.player.weapon else ""
            print(f"{i}. {item.name}{equipped} - {item.description}")

        choice = input("Enter item number to equip weapon, or press Enter to go back: ")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.player.inventory):
                item = self.player.inventory[idx]
                if isinstance(item, Weapon):
                    self.player.equip_weapon(item)
                else:
                    print("You can only equip weapons.")
            else:
                print("Invalid selection.")

    def riddle_challenge(self):
        """Present the player with a riddle for a potential reward."""
        riddle, answer = random.choice(RIDDLES)
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
