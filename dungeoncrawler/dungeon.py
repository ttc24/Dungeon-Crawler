import json
import os
import random

from .constants import SAVE_FILE, SCORE_FILE, ANNOUNCER_LINES, RIDDLES
from .entities import Player, Enemy, Companion
from .items import Item, Weapon

# Enemy stats keyed by name so floor configs can easily reference them
ENEMY_STATS = {
    "Goblin": (40, 70, 5, 12, 2),
    "Skeleton": (60, 90, 7, 14, 3),
    "Orc": (80, 110, 10, 18, 4),
    "Wraith": (100, 140, 12, 22, 6),
    "Demon": (120, 160, 15, 26, 8),
    "Bandit": (50, 80, 6, 14, 3),
    "Cultist": (65, 95, 9, 16, 3),
    "Ghoul": (70, 100, 8, 15, 4),
    "Vampire": (90, 130, 10, 20, 5),
    "Troll": (110, 150, 13, 23, 6),
    "Lich": (130, 170, 14, 26, 7),
    "Minotaur": (140, 180, 16, 28, 8),
    "Harpy": (70, 110, 10, 18, 4),
    "Werewolf": (100, 140, 12, 20, 5),
    "Gargoyle": (90, 130, 10, 22, 6),
    "Basilisk": (120, 160, 14, 24, 7),
    "Shade": (80, 120, 11, 19, 4),
    "Warlock": (110, 150, 15, 25, 6),
    "Zombie": (60, 100, 6, 14, 3),
    "Revenant": (150, 190, 18, 28, 9),
    "Phoenix": (160, 200, 20, 30, 10),
    "Giant Spider": (70, 110, 9, 17, 4),
    "Slime King": (130, 170, 13, 21, 6),
    "Hydra": (180, 220, 22, 32, 11),
    "Dark Knight": (170, 210, 21, 29, 10),
    "Cyclops": (190, 230, 24, 34, 12),
    "Beholder": (200, 240, 26, 36, 13),
    "Astral Dragon": (220, 260, 30, 40, 15),
    "Babababoon": (80, 120, 10, 20, 5),
    "Bactrian": (80, 120, 10, 20, 5),
    "Bad Llama": (80, 120, 10, 20, 5),
    "Big Boy Blue": (80, 120, 10, 20, 5),
    "Blender Fiend": (80, 120, 10, 20, 5),
    "Blister Ghoul": (80, 120, 10, 20, 5),
    "Blood and Ink Elemental": (80, 120, 10, 20, 5),
    "Brindle Grub": (80, 120, 10, 20, 5),
    "Bugaboo": (80, 120, 10, 20, 5),
    "Cave Mudge Bonker": (80, 120, 10, 20, 5),
    "Chee": (80, 120, 10, 20, 5),
    "Children of Inpewt": (80, 120, 10, 20, 5),
    "Chilly Goat": (80, 120, 10, 20, 5),
    "Clurichaun": (80, 120, 10, 20, 5),
    "Concierge Shark": (80, 120, 10, 20, 5),
    "Cornets": (80, 120, 10, 20, 5),
    "Crest": (80, 120, 10, 20, 5),
    "Danger Dingo": (80, 120, 10, 20, 5),
    "Demons": (80, 120, 10, 20, 5),
    "Drek": (80, 120, 10, 20, 5),
    "Experience (Mob)": (80, 120, 10, 20, 5),
    "Festering Ghoul": (80, 120, 10, 20, 5),
    "Flesher": (80, 120, 10, 20, 5),
    "Former Circus Lemur": (80, 120, 10, 20, 5),
    "Frenzied Gerbil": (80, 120, 10, 20, 5),
    "Ghommid": (80, 120, 10, 20, 5),
    "Glamoured Fragment": (80, 120, 10, 20, 5),
    "Goblin Bomb Bard": (80, 120, 10, 20, 5),
    "Goblin Engineer": (80, 120, 10, 20, 5),
    "Goblin Shamanka": (80, 120, 10, 20, 5),
    "Goblins": (80, 120, 10, 20, 5),
    "Gross Atomizers": (80, 120, 10, 20, 5),
    "Hellspawn Familiar": (80, 120, 10, 20, 5),
    "Hills Cyclops": (80, 120, 10, 20, 5),
    "Incubus": (80, 120, 10, 20, 5),
    "Jikininki Janitor Ghouls": (80, 120, 10, 20, 5),
    "Kobold": (80, 120, 10, 20, 5),
    "Krakaren Clone (Fourth Floor)": (80, 120, 10, 20, 5),
    "Krakaren Clone (Second Floor)": (80, 120, 10, 20, 5),
    "Krakaren Crotch Dumplings": (80, 120, 10, 20, 5),
    "Krasue": (80, 120, 10, 20, 5),
    "Kravyad": (80, 120, 10, 20, 5),
    "Laminak": (80, 120, 10, 20, 5),
    "Lesser Demon": (80, 120, 10, 20, 5),
    "Literal Fire Ants": (80, 120, 10, 20, 5),
    "Male Thorny Devil": (80, 120, 10, 20, 5),
    "ManTauR": (80, 120, 10, 20, 5),
    "Mind Horror": (80, 120, 10, 20, 5),
    "Mold Lion": (80, 120, 10, 20, 5),
    "Mongoliensis": (80, 120, 10, 20, 5),
    "Monk Seal": (80, 120, 10, 20, 5),
    "Naiad": (80, 120, 10, 20, 5),
    "Night Weasel": (80, 120, 10, 20, 5),
    "Octo-Shark": (80, 120, 10, 20, 5),
    "Odius Creeper": (80, 120, 10, 20, 5),
    "Ogre": (80, 120, 10, 20, 5),
    "Pain Amplifier Jellyfish": (80, 120, 10, 20, 5),
    "Pollyslog": (80, 120, 10, 20, 5),
    "Pooka": (80, 120, 10, 20, 5),
    "Pox Slug": (80, 120, 10, 20, 5),
    "Psycho Sticker": (80, 120, 10, 20, 5),
    "Pterolykos": (80, 120, 10, 20, 5),
    "Rage Elemental": (80, 120, 10, 20, 5),
    "Rat-kin": (80, 120, 10, 20, 5),
    "Rats": (80, 120, 10, 20, 5),
    "Razor Fox": (80, 120, 10, 20, 5),
    "Reaper Spider Minion": (80, 120, 10, 20, 5),
    "Rot Stickers": (80, 120, 10, 20, 5),
    "Satan's Lil' Hedgehog": (80, 120, 10, 20, 5),
    "Scat Thug": (80, 120, 10, 20, 5),
    "Scatterer": (80, 120, 10, 20, 5),
    "Shambling Acid Impaler": (80, 120, 10, 20, 5),
    "Shambling Berseker": (80, 120, 10, 20, 5),
    "Shock Chomper": (80, 120, 10, 20, 5),
    "Skellie": (80, 120, 10, 20, 5),
    "Skyfowl": (80, 120, 10, 20, 5),
    "Slime": (80, 120, 10, 20, 5),
    "Sluggalo": (80, 120, 10, 20, 5),
    "Squonk": (80, 120, 10, 20, 5),
    "Stone Hawk": (80, 120, 10, 20, 5),
    "Street Urchin": (80, 120, 10, 20, 5),
    "Succubus": (80, 120, 10, 20, 5),
    "Superior Fire Demon": (80, 120, 10, 20, 5),
    "Swordfish Interlopers": (80, 120, 10, 20, 5),
    "Terror the Clown": (80, 120, 10, 20, 5),
    "Troglodyte": (80, 120, 10, 20, 5),
    "Troglodyte Pygmy": (80, 120, 10, 20, 5),
    "Tummy Acher": (80, 120, 10, 20, 5),
    "Turkey": (80, 120, 10, 20, 5),
    "Tuskling": (80, 120, 10, 20, 5),
    "Unvaccinated Clurichaun Rev-Up Consultant": (80, 120, 10, 20, 5),
    "Ursine": (80, 120, 10, 20, 5),
    "Village Guard Swordsman": (80, 120, 10, 20, 5),
    "Vine Creepers": (80, 120, 10, 20, 5),
    "Visitor": (80, 120, 10, 20, 5),
    "Vorpal": (80, 120, 10, 20, 5),
    "Wall Monitor": (80, 120, 10, 20, 5),
    "War Mage": (80, 120, 10, 20, 5),
    "Wrath Ghouls": (80, 120, 10, 20, 5),
    "Zlurpies": (80, 120, 10, 20, 5),
}

# Special abilities for certain enemies
ENEMY_ABILITIES = {
    "Vampire": "lifesteal",
    "Wraith": "poison",
    "Dark Knight": "double_strike",
    "Lich": "lifesteal",
    "Warlock": "burn",
    "Werewolf": "double_strike",
    "Basilisk": "freeze",
    "Phoenix": "burn",
    "Hydra": "poison",
}

# Boss stats and loot tables keyed by name
BOSS_STATS = {
    "Bone Tyrant": (250, 30, 12, 120, "lifesteal"),
    "Inferno Golem": (270, 35, 14, 140, "burn"),
    "Frost Warden": (260, 28, 13, 130, "freeze"),
    "Shadow Reaver": (280, 33, 15, 150, "poison"),
    "Doom Bringer": (300, 38, 16, 160, "double_strike"),
    "Void Serpent": (290, 36, 17, 155, "poison"),
    "Ember Lord": (295, 37, 16, 158, "burn"),
    "Glacier Fiend": (265, 29, 14, 133, "freeze"),
    "Grave Monarch": (275, 32, 15, 138, "lifesteal"),
    "Storm Reaper": (285, 34, 15, 145, "double_strike"),
    "Asojano": (260, 35, 15, 150, None),
    "Ball of Swine": (260, 35, 15, 150, None),
    "Big Tina": (260, 35, 15, 150, None),
    "Boss": (260, 35, 15, 150, None),
    "Claude Sludgington the Fourth": (260, 35, 15, 150, None),
    "Denise": (260, 35, 15, 150, None),
    "Dismember": (260, 35, 15, 150, None),
    "Dispenser": (260, 35, 15, 150, None),
    "Feral Goose": (260, 35, 15, 150, None),
    "Ferdinand": (260, 35, 15, 150, None),
    "Gore-Gore": (260, 35, 15, 150, None),
    "Grimaldi": (260, 35, 15, 150, None),
    "Heather the Bear": (260, 35, 15, 150, None),
    "Hoarder": (260, 35, 15, 150, None),
    "Imogen": (260, 35, 15, 150, None),
    "Juicer": (260, 35, 15, 150, None),
    "Krakaren Clone (Fourth Floor)": (260, 35, 15, 150, None),
    "Krakaren Clone (Second Floor)": (260, 35, 15, 150, None),
    "Lusca": (260, 35, 15, 150, None),
    "Madre de Aguas": (260, 35, 15, 150, None),
    "Mrs. Ghazi": (260, 35, 15, 150, None),
    "Odious Creepers": (260, 35, 15, 150, None),
    "Pooka": (260, 35, 15, 150, None),
    "Quetzalcoatlus": (260, 35, 15, 150, None),
    "Ralph": (260, 35, 15, 150, None),
    "Reef Explorer": (260, 35, 15, 150, None),
    "Reminiscence Hydra of Malicious Compliance": (260, 35, 15, 150, None),
    "Ruckus": (260, 35, 15, 150, None),
    "Rude-Dolph the Blood-Nosed Slay-Deer": (260, 35, 15, 150, None),
    "Scolopendra": (260, 35, 15, 150, None),
    "Sentinel gun": (260, 35, 15, 150, None),
    "Shi Maria": (260, 35, 15, 150, None),
    "Sierra": (260, 35, 15, 150, None),
    "Station Mimic": (260, 35, 15, 150, None),
    "Thorn Room Boss Battle": (260, 35, 15, 150, None),
    "Tom": (260, 35, 15, 150, None),
}

BOSS_LOOT = {
    "Bone Tyrant": [Weapon("Skullcrusher", "A mace adorned with bone fragments.", 24, 32, 0)],
    "Inferno Golem": [Weapon("Molten Blade", "Red-hot sword that scorches foes.", 26, 34, 0)],
    "Frost Warden": [Weapon("Glacier Edge", "Chilling blade that slows enemies.", 23, 31, 0)],
    "Shadow Reaver": [Weapon("Nightfang", "A dagger that thrives in shadows.", 22, 30, 0)],
    "Doom Bringer": [Weapon("Cataclysm", "Heavy axe with devastating power.", 28, 36, 0)],
    "Void Serpent": [Weapon("Venom Spire", "Spear coated in lethal toxins.", 24, 32, 0)],
    "Ember Lord": [Weapon("Flame Lash", "Whip of living fire.", 25, 33, 0)],
    "Glacier Fiend": [Weapon("Frozen Talon", "Ice-forged claw that freezes.", 24, 31, 0)],
    "Grave Monarch": [Weapon("Cryptblade", "Blade of necrotic energy.", 25, 34, 0)],
    "Storm Reaper": [Weapon("Thunder Cleaver", "Sword crackling with lightning.", 26, 35, 0)],
}

# Floor specific configuration
FLOOR_CONFIGS = {
    1: {
        "size": (8, 8),
        "enemies": ["Goblin", "Skeleton", "Bandit"],
        "bosses": ["Bone Tyrant"],
        "places": {"Trap": 2, "Treasure": 2, "Enchantment": 1, "Sanctuary": 1, "Blacksmith": 1},
    },
    2: {
        "size": (9, 9),
        "enemies": ["Orc", "Cultist", "Ghoul", "Bandit"],
        "bosses": ["Inferno Golem", "Frost Warden"],
        "places": {"Trap": 3, "Treasure": 3, "Enchantment": 1, "Sanctuary": 1, "Blacksmith": 1},
    },
    3: {
        "size": (10, 10),
        "enemies": ["Vampire", "Warlock", "Wraith", "Werewolf"],
        "bosses": ["Shadow Reaver", "Doom Bringer"],
        "places": {"Trap": 3, "Treasure": 4, "Enchantment": 2, "Sanctuary": 2, "Blacksmith": 1},
    },
    4: {
        "size": (11, 11),
        "enemies": ["Basilisk", "Gargoyle", "Troll", "Lich"],
        "bosses": ["Void Serpent", "Ember Lord", "Glacier Fiend"],
        "places": {"Trap": 4, "Treasure": 4, "Enchantment": 2, "Sanctuary": 2, "Blacksmith": 1},
    },
    5: {
        "size": (12, 12),
        "enemies": ["Phoenix", "Hydra", "Revenant", "Beholder"],
        "bosses": ["Grave Monarch", "Storm Reaper"],
        "places": {"Trap": 4, "Treasure": 5, "Enchantment": 2, "Sanctuary": 2, "Blacksmith": 1},
    },
    6: {
        "size": (13, 13),
        "enemies": ["Minotaur", "Demon", "Harpy", "Shade"],
        "bosses": ["Bone Tyrant", "Inferno Golem"],
        "places": {"Trap": 5, "Treasure": 5, "Enchantment": 2, "Sanctuary": 2, "Blacksmith": 1},
    },
    7: {
        "size": (14, 14),
        "enemies": ["Giant Spider", "Slime King", "Zombie", "Gargoyle"],
        "bosses": ["Frost Warden", "Shadow Reaver"],
        "places": {"Trap": 5, "Treasure": 6, "Enchantment": 2, "Sanctuary": 2, "Blacksmith": 1},
    },
    8: {
        "size": (15, 15),
        "enemies": ["Dark Knight", "Cyclops", "Basilisk", "Werewolf"],
        "bosses": ["Doom Bringer", "Void Serpent"],
        "places": {"Trap": 5, "Treasure": 6, "Enchantment": 3, "Sanctuary": 2, "Blacksmith": 1},
    },
    9: {
        "size": (15, 15),
        "enemies": ["Hydra", "Beholder", "Revenant", "Warlock"],
        "bosses": ["Ember Lord", "Glacier Fiend"],
        "places": {"Trap": 6, "Treasure": 6, "Enchantment": 3, "Sanctuary": 2, "Blacksmith": 1},
    },
    10: {
        "size": (15, 15),
        "enemies": ["Phoenix", "Dark Knight", "Cyclops", "Minotaur"],
        "bosses": ["Grave Monarch", "Storm Reaper"],
        "places": {"Trap": 6, "Treasure": 7, "Enchantment": 3, "Sanctuary": 3, "Blacksmith": 1},
    },
    11: {
        "size": (15, 15),
        "enemies": ["Astral Dragon", "Demon", "Harpy", "Shade"],
        "bosses": ["Bone Tyrant", "Inferno Golem", "Frost Warden"],
        "places": {"Trap": 7, "Treasure": 7, "Enchantment": 3, "Sanctuary": 3, "Blacksmith": 1},
    },
    12: {
        "size": (15, 15),
        "enemies": ["Giant Spider", "Slime King", "Zombie", "Warlock"],
        "bosses": ["Shadow Reaver", "Doom Bringer", "Void Serpent"],
        "places": {"Trap": 7, "Treasure": 8, "Enchantment": 4, "Sanctuary": 3, "Blacksmith": 1},
    },
    13: {
        "size": (15, 15),
        "enemies": ["Basilisk", "Gargoyle", "Troll", "Lich"],
        "bosses": ["Ember Lord", "Glacier Fiend", "Grave Monarch"],
        "places": {"Trap": 8, "Treasure": 8, "Enchantment": 4, "Sanctuary": 3, "Blacksmith": 1},
    },
    14: {
        "size": (15, 15),
        "enemies": ["Hydra", "Beholder", "Revenant", "Dark Knight"],
        "bosses": ["Storm Reaper"],
        "places": {"Trap": 8, "Treasure": 9, "Enchantment": 4, "Sanctuary": 3, "Blacksmith": 1},
    },
    15: {
        "size": (15, 15),
        "enemies": ["Cyclops", "Astral Dragon", "Phoenix", "Minotaur"],
        "bosses": ["Doom Bringer", "Void Serpent"],
        "places": {"Trap": 9, "Treasure": 9, "Enchantment": 5, "Sanctuary": 3, "Blacksmith": 1},
    },
    16: {
        "size": (15, 15),
        "enemies": ["Demon", "Harpy", "Shade", "Giant Spider"],
        "bosses": ["Ember Lord", "Glacier Fiend"],
        "places": {"Trap": 9, "Treasure": 10, "Enchantment": 5, "Sanctuary": 3, "Blacksmith": 1},
    },
    17: {
        "size": (15, 15),
        "enemies": ["Slime King", "Zombie", "Gargoyle", "Warlock"],
        "bosses": ["Grave Monarch", "Storm Reaper"],
        "places": {"Trap": 9, "Treasure": 10, "Enchantment": 5, "Sanctuary": 4, "Blacksmith": 1},
    },
    18: {
        "size": (15, 15),
        "enemies": ["Hydra", "Beholder", "Astral Dragon", "Dark Knight"],
        "bosses": ["Bone Tyrant", "Doom Bringer", "Void Serpent"],
        "places": {"Trap": 10, "Treasure": 10, "Enchantment": 6, "Sanctuary": 4, "Blacksmith": 1},
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
        self.room_names = [[self.generate_room_name() for _ in range(width)] for _ in range(height)]
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
            Weapon("Crossbow", "Ranged attack with bolts", 11, 19, 60)
        ]
        self.rare_loot = [
            Weapon("Elven Longbow", "Bow of unmatched accuracy.", 15, 25, 0),
            Item("Blessed Charm", "Said to bring good fortune."),
            Weapon("Dwarven Waraxe", "Forged in the deep halls.", 12, 20, 0),
            Item("Shadow Cloak", "Grants an air of mystery")
        ]

    def announce(self, msg):
        print(f"[Announcer] {random.choice(ANNOUNCER_LINES)} {msg}")

    def save_game(self, floor):
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
            }
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE) as f:
                data = json.load(f)
            self.player = Player(data["player"]["name"], data["player"].get("class", "Warrior"))
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
            return data.get("floor", 1)
        return 1

    def record_score(self, floor):
        records = []
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE) as f:
                records = json.load(f)
        records.append({"name": self.player.name, "score": self.player.get_score(), "floor": floor})
        records = sorted(records, key=lambda x: x["score"], reverse=True)[:10]
        with open(SCORE_FILE, "w") as f:
            json.dump(records, f, indent=2)
        print("-- Leaderboard --")
        for r in records:
            print(f"{r['name']}: {r['score']} (Floor {r.get('floor', '?')})")

    def offer_guild(self):
        if self.player.guild:
            return
        print("Guilds now accept new members!")
        print("1. Warriors' Guild - Bonus Health")
        print("2. Mages' Guild - Bonus Attack")
        print("3. Rogues' Guild - Faster Skills")
        choice = input("Join which guild? (1/2/3 or skip): ")
        guilds = {"1": "Warriors' Guild", "2": "Mages' Guild", "3": "Rogues' Guild"}
        if choice in guilds:
            self.player.join_guild(guilds[choice])

    def offer_race(self):
        if self.player.race:
            return
        print("New races are available to you!")
        print("1. Human 2. Elf 3. Dwarf 4. Orc 5. Gnome 6. Halfling 7. Catfolk 8. Lizardfolk")
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
        }
        race = races.get(choice, "Human")
        self.player.choose_race(race)

    def generate_room_name(self, room_type=None):
        lore = {
            "Treasure": ("Glittering Vault", "The air shimmers with unseen magic. Ancient riches may lie within."),
            "Trap": ("Booby-Trapped Passage", "This corridor is riddled with pressure plates and crumbled bones."),
            "Enemy": ("Cursed Hall", "The shadows shift... something watches from the dark."),
            "Exit": ("Sealed Gate", "Massive stone doors sealed by arcane runes. It might be the only way out."),
            "Key": ("Hidden Niche", "A hollow carved into the wall, forgotten by time. Something valuable glints inside."),
            "Sanctuary": ("Sacred Sanctuary", "A calm aura fills this room, soothing your wounds."),
            "Empty": ("Silent Chamber", "Dust covers everything. It appears long abandoned."),
            "default": (None, None)
        }

        if room_type in lore:
            return lore[room_type][0]

        adjectives = [
            "Collapsed", "Echoing", "Gloomy", "Withered", "Fungal", "Whispering", "Icy",
            "Dust-choked", "Ancient", "Haunted", "Buried", "Broken", "Wretched", "Twisting"
        ]
        nouns = [
            "Passage", "Fissure", "Grotto", "Vault", "Sanctum", "Shrine",
            "Cellar", "Refuge", "Gallery", "Crypt", "Atrium", "Chapel", "Workshop", "Quarters"
        ]
        return f"{random.choice(adjectives)} {random.choice(nouns)}"

    def generate_dungeon(self, floor=1):
        cfg = FLOOR_CONFIGS.get(floor, {})
        size = cfg.get("size", (min(15, 8 + floor), min(15, 8 + floor)))
        self.width, self.height = size
        self.rooms = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.room_names = [[self.generate_room_name() for _ in range(self.width)] for _ in range(self.height)]
        visited = set()
        path = []
        x, y = self.width // 2, self.height // 2
        start = (x, y)
        visited.add(start)
        path.append(start)

        while len(visited) < (self.width * self.height) // 2:
            direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            nx, ny = x + direction[0], y + direction[1]
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    path.append((nx, ny))
                x, y = nx, ny

        for (x, y) in visited:
            self.rooms[y][x] = "Empty"

        if self.player is None:
            name = input("Enter your name: ")
            print("Choose your class: 1. Warrior 2. Mage 3. Rogue 4. Cleric 5. Paladin 6. Bard")
            choice = input("Class: ")
            classes = {
                "1": "Warrior",
                "2": "Mage",
                "3": "Rogue",
                "4": "Cleric",
                "5": "Paladin",
                "6": "Bard",
            }
            class_type = classes.get(choice, "Warrior")
            self.player = Player(name, class_type)
            print(f"Welcome {self.player.name} the {class_type}! Try not to die horribly.")
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

        enemy_names = cfg.get("enemies", list(ENEMY_STATS.keys()))
        early_game_bonus = 5 if floor <= 3 else 0
        for _ in range(5 + floor):
            name = random.choice(enemy_names)
            hp_min, hp_max, atk_min, atk_max, defense = ENEMY_STATS[name]

            hp_scale = 1 if floor <= 3 else 2
            atk_scale = 1 if floor <= 3 else 2

            defense = max(1, defense + floor // 3)

            health = random.randint(hp_min + floor * hp_scale, hp_max + floor * hp_scale)
            attack = random.randint(atk_min + atk_scale, atk_max + atk_scale)
            gold = random.randint(15 + early_game_bonus + floor, 30 + floor * 2)

            ability = ENEMY_ABILITIES.get(name)
            enemy = Enemy(name, health, attack, defense, gold, ability)
            enemy.xp = max(5, (health + attack + defense) // 15)

            place(enemy)

        boss_names = cfg.get("bosses", list(BOSS_STATS.keys()))
        name = random.choice(boss_names)
        hp, atk, dfs, gold, ability = BOSS_STATS[name]
        print(f"A powerful boss guards this floor! The {name} lurks nearby...")
        boss = Enemy(name, hp + floor * 10, atk + floor, dfs + floor // 2, gold + floor * 5, ability=ability)
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
        default_places = {"Trap": 3, "Treasure": 3, "Enchantment": 2, "Sanctuary": 2, "Blacksmith": 1}
        place_counts = default_places.copy()
        place_counts.update(cfg.get("places", {}))
        for pname, count in place_counts.items():
            for _ in range(count):
                place(pname)
        # Key is now tied to boss drop; don't place it separately

    def play_game(self):
        floor = self.load_game()
        if self.player:
            cont = input("Continue your last adventure? (y/n): ")
            if cont.lower() != "y":
                self.player = None
                floor = 1
        print("Welcome to Dungeon Crawler!")
        while (self.player is None or self.player.is_alive()) and floor <= 18:
            print(f"===== Entering Floor {floor} =====")
            self.generate_dungeon(floor)
            self.trigger_floor_event(floor)

            while self.player.is_alive():
                print(f"Position: ({self.player.x}, {self.player.y}) - {self.room_names[self.player.y][self.player.x]}")
                print(f"Health: {self.player.health} | XP: {self.player.xp} | Gold: {self.player.gold} | Level: {self.player.level} | Floor: {floor} | Skill CD: {self.player.skill_cooldown}")
                if self.player.guild:
                    print(f"Guild: {self.player.guild}")
                if self.player.race:
                    print(f"Race: {self.player.race}")
                print("1. Move Left 2. Move Right 3. Move Up 4. Move Down 5. Visit Shop 6. Inventory 7. Quit")
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
                else:
                    print("Invalid choice!")

                if self.player.level >= 5 and self.player.health < self.player.max_health:
                    self.player.health += 1

                if self.player.x == self.exit_coords[0] and self.player.y == self.exit_coords[1] and self.player.has_item("Key"):
                    print("You reach the Sealed Gate.")
                    proceed = input("Would you like to descend to the next floor? (y/n): ").lower()
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
        dx, dy = {"left": (-1,0), "right": (1,0), "up": (0,-1), "down": (0,1)}.get(direction, (0,0))
        x, y = self.player.x + dx, self.player.y + dy
        if 0 <= x < self.width and 0 <= y < self.height and self.rooms[y][x] is not None:
            self.handle_room(x, y)
        else:
            print("You can't move that way.")

    def handle_room(self, x, y):
        room = self.rooms[y][x]
        name = self.room_names[y][x]
        lore = {
            "Glittering Vault": "The air shimmers with unseen magic. Ancient riches may lie within.",
            "Booby-Trapped Passage": "This corridor is riddled with pressure plates and crumbled bones.",
            "Cursed Hall": "The shadows shift... something watches from the dark.",
            "Sealed Gate": "Massive stone doors sealed by arcane runes. It might be the only way out.",
            "Hidden Niche": "A hollow carved into the wall, forgotten by time. Something valuable glints inside.",
            "Silent Chamber": "Dust covers everything. It appears long abandoned.",
            "Sacred Sanctuary": "A peaceful place that heals weary adventurers."
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
                    print("Your weapon is already enchanted! You can't add another enchantment.")
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
                print(f"Your weapon: {self.player.weapon.name} ({self.player.weapon.min_damage}-{self.player.weapon.max_damage})")
                print("Would you like to upgrade your weapon for 50 gold? +3 min/max damage")
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
                print("The blacksmith scoffs. 'No weapon? Come back when you have something worth forging.'")
            self.rooms[y][x] = None
            self.room_names[y][x] = "Blacksmith Forge"

        elif room == "Sanctuary":
            self.player.health = self.player.max_health
            print("A soothing warmth envelops you. Your wounds are fully healed.")
            self.rooms[y][x] = None
            self.room_names[y][x] = "Sacred Sanctuary"

        elif room == "Trap":
            riddle, answer = random.choice(RIDDLES)
            print("A trap springs! Solve this riddle to escape unharmed:")
            print(riddle)
            response = input("Answer: ").strip().lower()
            if response == answer:
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
        print(f"You encountered a {enemy.name}! {enemy.ability.capitalize() if enemy.ability else ''} Boss incoming!")
        self.announce(f"{self.player.name} engages {enemy.name}!")
        while self.player.is_alive() and enemy.is_alive():
            self.player.apply_status_effects()
            if 'freeze' in self.player.status_effects:
                print("\u2744\ufe0f You are frozen and skip this turn!")
                self.player.status_effects['freeze'] -= 1
                if self.player.status_effects['freeze'] <= 0:
                    del self.player.status_effects['freeze']
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

    def shop(self):
        print("Welcome to the Shop!")
        print(f"Gold: {self.player.gold}")
        for i, item in enumerate(self.shop_items, 1):
            price = item.price if isinstance(item, Weapon) else 10
            print(f"{i}. {item.name} - {price} Gold")
        print(f"{len(self.shop_items)+1}. Exit")

        choice = input("Buy what?")
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
            elif choice == len(self.shop_items) + 1:
                print("Leaving the shop.")
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

    # Floor-specific events keep gameplay varied without hardcoding logic in
    # play_game. Additional floors can be added here easily.
    def trigger_floor_event(self, floor):
        events = {
            1: self._floor_one_event,
            2: self._floor_two_event,
            3: self._floor_three_event,
            5: self._floor_five_event,
        }
        if floor in events:
            events[floor]()

    def _floor_one_event(self):
        print("The crowd roars as you step into the arena for the first time.")

    def _floor_two_event(self):
        self.offer_guild()

    def _floor_three_event(self):
        self.offer_race()

    def _floor_five_event(self):
        print("A mysterious merchant sets up shop, selling exotic wares.")
