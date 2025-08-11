"""Core game objects for the dungeon crawler.

Historically this module contained combat, map generation and shop logic in
one monolithic file.  Those responsibilities now live in dedicated modules:

``dungeoncrawler.combat``  -- battle mechanics
``dungeoncrawler.map``     -- dungeon generation and movement
``dungeoncrawler.shop``    -- buying and selling items

The :class:`DungeonBase` class orchestrates these pieces and provides the
high level game flow used by the tests.
"""

from __future__ import annotations

import json
import os
import random

from .constants import SAVE_FILE, SCORE_FILE, ANNOUNCER_LINES, RIDDLES
from .entities import Player, Enemy, Companion
from .items import Item, Weapon
from . import map as dungeon_map
from . import shop as shop_module


class DungeonBase:
    """Core engine for running the dungeon crawler game."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rooms = [[None for _ in range(width)] for _ in range(height)]
        self.room_names = [
            [dungeon_map.generate_room_name() for _ in range(width)]
            for _ in range(height)
        ]
        self.visited_rooms = set()
        self.player: Player | None = None
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

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def announce(self, msg: str) -> None:
        print(f"[Announcer] {random.choice(ANNOUNCER_LINES)} {msg}")

    def save_game(self, floor: int) -> None:
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

    def load_game(self) -> int:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE) as f:
                data = json.load(f)
            self.player = Player(data["player"]["name"], data["player"].get("class", "Novice"))
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

    def record_score(self, floor: int) -> None:
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

    # ------------------------------------------------------------------
    # Character customisation offers
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Main gameplay loop
    # ------------------------------------------------------------------

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
            dungeon_map.generate_dungeon(self, floor)
            self.trigger_floor_event(floor)

            while self.player.is_alive():
                print(
                    f"Position: ({self.player.x}, {self.player.y}) - {self.room_names[self.player.y][self.player.x]}"
                )
                print(
                    f"Health: {self.player.health} | XP: {self.player.xp} | Gold: {self.player.gold} | "
                    f"Level: {self.player.level} | Floor: {floor} | Skill CD: {self.player.skill_cooldown}"
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
                    dungeon_map.move_player(self, "left")
                elif choice == "2":
                    dungeon_map.move_player(self, "right")
                elif choice == "3":
                    dungeon_map.move_player(self, "up")
                elif choice == "4":
                    dungeon_map.move_player(self, "down")
                elif choice == "5":
                    shop_module.shop(self)
                elif choice == "6":
                    self.show_inventory()
                elif choice == "7":
                    print("Thanks for playing!")
                    return
                elif choice == "8":
                    dungeon_map.render_map(self)
                else:
                    print("Invalid choice!")

                if self.player.level >= 5 and self.player.health < self.player.max_health:
                    self.player.health += 1

                if (
                    self.player.x == self.exit_coords[0]
                    and self.player.y == self.exit_coords[1]
                    and self.player.has_item("Key")
                ):
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

    # ------------------------------------------------------------------
    # Misc helpers used by map and events
    # ------------------------------------------------------------------

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

    def grant_inspiration(self, turns: int = 3):
        """Give the player a temporary inspire buff."""

        self.player.status_effects["inspire"] = turns

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

    # ------------------------------------------------------------------
    # Floor events
    # ------------------------------------------------------------------

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
        shop_module.shop(self)

    def _floor_fifteen_event(self):
        print("A robed sage blocks your path, offering a riddle challenge.")
        self.riddle_challenge()

