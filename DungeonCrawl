import random

# --- Entity Classes ---

class Entity:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Player(Entity):
    def __init__(self, name):
        super().__init__(name, "The player")
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.xp = 0
        self.gold = 0
        self.inventory = []
        self.weapon = None
        self.status_effects = {}  # Tracks status effects like poison
        self.x = 0
        self.y = 0

    def is_alive(self):
        return self.health > 0

    def collect_item(self, item):
        self.inventory.append(item)

    def has_item(self, name):
        return any(item.name == name for item in self.inventory)

    def use_health_potion(self):
        potion = next((item for item in self.inventory if isinstance(item, Item) and item.name == "Health Potion"), None)
        if potion:
            self.inventory.remove(potion)
            healed_amount = min(20, self.max_health - self.health)
            self.health += healed_amount
            print(f"You used a Health Potion and gained {healed_amount} health.")
        else:
            print("You don't have a Health Potion to use.")

    def attack(self, enemy):
        damage = self.calculate_damage()
        self.apply_weapon_effect(enemy)
        print(f"You attacked the {enemy.name} and dealt {damage} damage!")
        enemy.take_damage(damage)

        if not enemy.is_alive():
            self.process_enemy_defeat(enemy)

    def calculate_damage(self):
        if self.weapon:
            return random.randint(self.weapon.min_damage, self.weapon.max_damage)
        return random.randint(self.attack_power // 2, self.attack_power)

    def apply_weapon_effect(self, enemy):
        if self.weapon and hasattr(self.weapon, 'effect') and self.weapon.effect:
            effect = self.weapon.effect
            enemy.status_effects = getattr(enemy, 'status_effects', {})
            enemy.status_effects[effect] = 3
            print(f"Your weapon inflicts {effect} on the {enemy.name}!")

    def process_enemy_defeat(self, enemy):
        self.xp += enemy.xp
        gold_dropped = enemy.drop_gold()
        if self.level >= 3:
            gold_dropped += 5
        self.gold += gold_dropped
        print(f"You defeated the {enemy.name}!")
        print(f"You gained {enemy.xp} XP and {gold_dropped} gold.")
        while self.xp >= self.level * 20:
            self.xp -= self.level * 20
            self.level_up()

    def defend(self, enemy):
        damage = max(0, enemy.attack_power - 5)
        self.health -= damage
        print(f"The {enemy.name} attacked you and dealt {damage} damage.")

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def apply_status_effects(self):
        if 'poison' in self.status_effects:
            poison_turns = self.status_effects['poison']
            if poison_turns > 0:
                self.health -= 3
                print("You take 3 poison damage!")
                self.status_effects['poison'] -= 1
            if self.status_effects['poison'] <= 0:
                del self.status_effects['poison']
        if 'burn' in self.status_effects:
            burn_turns = self.status_effects['burn']
            if burn_turns > 0:
                self.health -= 4
                print("You suffer 4 burn damage!")
                self.status_effects['burn'] -= 1
            if self.status_effects['burn'] <= 0:
                del self.status_effects['burn']
        if 'freeze' in self.status_effects:
            freeze_turns = self.status_effects['freeze']
            if freeze_turns > 0:
                print("You're frozen and lose your turn!")
                self.status_effects['freeze'] -= 1
            if self.status_effects['freeze'] <= 0:
                del self.status_effects['freeze']

    def level_up(self):
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
        self.attack_power += 3

        print(f"\nYou leveled up to level {self.level}!")
        print(f"Max Health increased to {self.max_health}")
        print(f"Attack Power increased to {self.attack_power}")

        if self.level == 3:
            print("You've unlocked Gold Finder: +5 gold after each kill.")
        if self.level == 5:
            print("You've unlocked Passive Regen: Heal 1 HP per move.")

    def equip_weapon(self, weapon):
        if weapon in self.inventory and isinstance(weapon, Weapon):
            if self.weapon:
                self.inventory.append(self.weapon)
                print(f"You unequipped the {self.weapon.name}")
            self.weapon = weapon
            self.inventory.remove(weapon)
            print(f"You equipped the {weapon.name}")
        else:
            print("You don't have a valid weapon to equip.")

    def get_score(self):
        return self.level * 100 + len(self.inventory) * 10 + self.gold

# --- Other Game Objects ---

class Enemy(Entity):
    def __init__(self, name, health, attack_power, defense, gold, ability=None):
        super().__init__(name, "")
        self.health = health
        self.attack_power = attack_power
        self.defense = defense
        self.gold = gold
        self.ability = ability
        self.xp = 10

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def drop_gold(self):
        return self.gold

    def attack(self, player):
        damage = random.randint(self.attack_power // 2, self.attack_power)
        if self.ability == "lifesteal":
            self.health += damage // 3
            print(f"The {self.name} drains life and heals for {damage // 3}!")
        elif self.ability == "poison":
            player.status_effects['poison'] = 3
        elif self.ability == "burn":
            player.status_effects['burn'] = 3
        elif self.ability == "freeze":
            player.status_effects['freeze'] = 1
            print(f"The {self.name} freezes you for 3 turns!")
        elif self.ability == "double_strike" and random.random() < 0.25:
            print(f"The {self.name} strikes twice!")
            player.take_damage(damage)
        player.take_damage(damage)
        print(f"The {self.name} attacked you and dealt {damage} damage.")

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Weapon(Item):
    def __init__(self, name, description, min_damage, max_damage, price=50):
        super().__init__(name, description)
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.price = price
        self.effect = None

# --- Dungeon System ---

class DungeonBase:
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
            Weapon("Flame Blade", "Glows with searing heat", 13, 20, 95)
        ]

    def generate_room_name(self, room_type=None):
        lore = {
            "Treasure": ("Glittering Vault", "The air shimmers with unseen magic. Ancient riches may lie within."),
            "Trap": ("Booby-Trapped Passage", "This corridor is riddled with pressure plates and crumbled bones."),
            "Enemy": ("Cursed Hall", "The shadows shift... something watches from the dark."),
            "Exit": ("Sealed Gate", "Massive stone doors sealed by arcane runes. It might be the only way out."),
            "Key": ("Hidden Niche", "A hollow carved into the wall, forgotten by time. Something valuable glints inside."),
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
        enchantment_rooms = ["Enchantment Chamber", "Alchemist's Forge"]
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

        self.player = Player(input("Enter your name: "))
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

        enemy_types = [
            ("Goblin", 40, 70, 5, 12, 2),
            ("Skeleton", 60, 90, 7, 14, 3),
            ("Orc", 80, 110, 10, 18, 4),
            ("Wraith", 100, 140, 12, 22, 6),
            ("Demon", 120, 160, 15, 26, 8),
            ("Bandit", 50, 80, 6, 14, 3),
            ("Cultist", 65, 95, 9, 16, 3),
            ("Ghoul", 70, 100, 8, 15, 4),
            ("Vampire", 90, 130, 10, 20, 5),
            ("Troll", 110, 150, 13, 23, 6),
            ("Lich", 130, 170, 14, 26, 7),
            ("Minotaur", 140, 180, 16, 28, 8),
            ("Harpy", 70, 110, 10, 18, 4),
            ("Werewolf", 100, 140, 12, 20, 5),
            ("Gargoyle", 90, 130, 10, 22, 6),
            ("Basilisk", 120, 160, 14, 24, 7),
            ("Shade", 80, 120, 11, 19, 4),
            ("Warlock", 110, 150, 15, 25, 6),
            ("Zombie", 60, 100, 6, 14, 3),
            ("Revenant", 150, 190, 18, 28, 9),
            ("Phoenix", 160, 200, 20, 30, 10),
            ("Giant Spider", 70, 110, 9, 17, 4),
            ("Slime King", 130, 170, 13, 21, 6),
            ("Hydra", 180, 220, 22, 32, 11),
            ("Dark Knight", 170, 210, 21, 29, 10)
        ]

        early_game_bonus = 5 if floor <= 3 else 0
        for _ in range(5 + floor):
            if floor >= 14:
                name, hp_min, hp_max, atk_min, atk_max, defense = enemy_types[-1]
            else:
                idx = min((floor - 1) // 3, len(enemy_types) - 2)
                name, hp_min, hp_max, atk_min, atk_max, defense = enemy_types[idx]

            hp_scale = 1 if floor <= 3 else 2
            atk_scale = 1 if floor <= 3 else 2

            defense = max(1, defense + floor // 3)

            health = random.randint(hp_min + floor * hp_scale, hp_max + floor * hp_scale)
            attack = random.randint(atk_min + atk_scale, atk_max + atk_scale)
            gold = random.randint(15 + early_game_bonus + floor, 30 + floor * 2)

            special_abilities = {
                "Vampire": "lifesteal",
                "Wraith": "poison",
                "Dark Knight": "double_strike",
                "Lich": "lifesteal",
                "Warlock": "burn",
                "Werewolf": "double_strike",
                "Basilisk": "freeze",
                "Phoenix": "burn",
                "Hydra": "poison"
            }
            ability = special_abilities.get(name)
            enemy = Enemy(name, health, attack, defense, gold, ability)
            enemy.xp = max(5, (health + attack + defense) // 15)

            place(enemy)

        boss_options = [
                ("Bone Tyrant", 250, 30, 12, 120, "lifesteal"),
                ("Inferno Golem", 270, 35, 14, 140, "burn"),
                ("Frost Warden", 260, 28, 13, 130, "freeze"),
                ("Shadow Reaver", 280, 33, 15, 150, "poison"),
                ("Doom Bringer", 300, 38, 16, 160, "double_strike"),
                ("Void Serpent", 290, 36, 17, 155, "poison"),
                ("Ember Lord", 295, 37, 16, 158, "burn"),
                ("Glacier Fiend", 265, 29, 14, 133, "freeze"),
                ("Grave Monarch", 275, 32, 15, 138, "lifesteal"),
                ("Storm Reaper", 285, 34, 15, 145, "double_strike")
            ]
        boss_choice = random.choice(boss_options)
        name, hp, atk, dfs, gold, ability = boss_choice
        print(f"A powerful boss guards this floor! The {name} lurks nearby...")
        boss = Enemy(name, hp + floor * 10, atk + floor, dfs + floor // 2, gold + floor * 5, ability=ability)
        place(boss)
        boss_loot_tables = {
                "Bone Tyrant": [Weapon("Skullcrusher", "A mace adorned with bone fragments.", 24, 32, 0)],
                "Inferno Golem": [Weapon("Molten Blade", "Red-hot sword that scorches foes.", 26, 34, 0)],
                "Frost Warden": [Weapon("Glacier Edge", "Chilling blade that slows enemies.", 23, 31, 0)],
                "Shadow Reaver": [Weapon("Nightfang", "A dagger that thrives in shadows.", 22, 30, 0)],
                "Doom Bringer": [Weapon("Cataclysm", "Heavy axe with devastating power.", 28, 36, 0)],
                "Void Serpent": [Weapon("Venom Spire", "Spear coated in lethal toxins.", 24, 32, 0)],
                "Ember Lord": [Weapon("Flame Lash", "Whip of living fire.", 25, 33, 0)],
                "Glacier Fiend": [Weapon("Frozen Talon", "Ice-forged claw that freezes.", 24, 31, 0)],
                "Grave Monarch": [Weapon("Cryptblade", "Blade of necrotic energy.", 25, 34, 0)],
                "Storm Reaper": [Weapon("Thunder Cleaver", "Sword crackling with lightning.", 26, 35, 0)]
            }
        boss_drop = boss_loot_tables.get(name, [])
        if boss_drop and random.random() < 0.5:
            loot = random.choice(boss_drop)
            print(f"✨ The boss dropped a unique weapon: {loot.name}!")
            place(loot)
            
            place(Item("Key", "A magical key dropped by the boss"))
        for _ in range(3):
            place("Trap")
        for _ in range(3):
            place("Treasure")
        for _ in range(2):
            place("Enchantment")
        place("Blacksmith")
        # Key is now tied to boss drop; don't place it separately

    def play_game(self):
        floor = 1
        while (self.player is None or self.player.is_alive()) and floor <= 18:
            print(f"===== Entering Floor {floor} =====")
            self.generate_dungeon(floor)

            while self.player.is_alive():
                print(f"Position: ({self.player.x}, {self.player.y}) - {self.room_names[self.player.y][self.player.x]}")
                print(f"Health: {self.player.health} | XP: {self.player.xp} | Gold: {self.player.gold} | Level: {self.player.level} | Floor: {floor}")
                print("1. Move Left 2. Move Right 3. Move Up 4. Move Down 5. Visit Shop 6. Inventory 7. Quit")
                choice = input("Action: ")

                if choice == "1": self.move_player("left")
                elif choice == "2": self.move_player("right")
                elif choice == "3": self.move_player("up")
                elif choice == "4": self.move_player("down")
                elif choice == "5": self.shop()
                elif choice == "6": self.show_inventory()
                elif choice == "7": print("Thanks for playing!"); return
                else: print("Invalid choice!")

                if self.player.level >= 5 and self.player.health < self.player.max_health:
                    self.player.health += 1

                if self.player.x == self.exit_coords[0] and self.player.y == self.exit_coords[1] and self.player.has_item("Key"):
                    print("You reach the Sealed Gate.")
                    proceed = input("Would you like to descend to the next floor? (y/n): ").lower()
                    if proceed == "y":
                        floor += 1
                        break
                    else:
                        print("You chose to exit the dungeon.")
                        print(f"Final Score: {self.player.get_score()}")
                        return

        print("You have died. Game Over!")
        print(f"Final Score: {self.player.get_score()}")

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
            "Silent Chamber": "Dust covers everything. It appears long abandoned."
        }
        if name in lore:
            print(f"{lore[name]}")

        if isinstance(room, Enemy):
            self.battle(room)
            if not room.is_alive():
                self.rooms[y][x] = None
        elif isinstance(room, Item):
            print(f"You found a {room.name}!")
            self.player.collect_item(room)
            self.rooms[y][x] = None
            if room.name == "Key":
                self.room_names[y][x] = "Hidden Niche"
        elif room == "Treasure":
            gold = random.randint(20, 50)
            self.player.gold += gold
            print(f"You found a treasure chest with {gold} gold!")
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

        elif room == "Trap":
            damage = random.randint(10, 30)
            self.player.take_damage(damage)
            print(f"It's a trap! You took {damage} damage.")
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

    def battle(self, enemy):
        print(f"You encountered a {enemy.name}! {enemy.ability.capitalize() if enemy.ability else ''} Boss incoming!")
        self.player.apply_status_effects()
        if 'freeze' in self.player.status_effects:
            print("\u2744\ufe0f You are frozen and skip this turn!")
            self.player.status_effects['freeze'] -= 1
            if self.player.status_effects['freeze'] <= 0:
                del self.player.status_effects['freeze']
            if enemy.is_alive():
                enemy.attack(self.player)
            return

        while self.player.is_alive() and enemy.is_alive():
            print(f"Player Health: {self.player.health}")
            print(f"Enemy Health: {enemy.health}")
            print("1. Attack\n2. Defend\n3. Use Health Potion")
            choice = input("Choose action: ")
            if choice == "1":
                self.player.attack(enemy)
                if enemy.is_alive():
                    enemy.attack(self.player)
            elif choice == "2":
                self.player.defend(enemy)
                if enemy.is_alive():
                    enemy.attack(self.player)
            elif choice == "3":
                self.player.use_health_potion()
                if enemy.is_alive():
                    enemy.attack(self.player)
            else:
                print("Invalid choice!")

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

if __name__ == "__main__":
    game = DungeonBase(10, 10)
    game.play_game()
