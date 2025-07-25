import random
from .items import Item, Weapon
from .constants import ANNOUNCER_LINES

class Entity:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Player(Entity):
    """Represents the hero controlled by the player.

    Tracks stats, inventory and equipped weapon while providing combat
    actions such as :meth:`attack`, :meth:`defend`, :meth:`use_health_potion`
    and :meth:`use_skill`. Leveling and character progression are handled via
    :meth:`level_up`, :meth:`join_guild` and :meth:`choose_race`.
    """
    def __init__(self, name, class_type="Warrior"):
        super().__init__(name, "The player")
        self.class_type = class_type
        if class_type == "Mage":
            self.level = 1
            self.health = 80
            self.max_health = 80
            self.attack_power = 14
        elif class_type == "Rogue":
            self.level = 1
            self.health = 90
            self.max_health = 90
            self.attack_power = 12
        elif class_type == "Cleric":
            self.level = 1
            self.health = 110
            self.max_health = 110
            self.attack_power = 9
        elif class_type == "Paladin":
            self.level = 1
            self.health = 120
            self.max_health = 120
            self.attack_power = 11
        elif class_type == "Bard":
            self.level = 1
            self.health = 90
            self.max_health = 90
            self.attack_power = 10
        else:
            # Default to Warrior stats
            self.level = 1
            self.health = 100
            self.max_health = 100
            self.attack_power = 10
        self.xp = 0
        self.gold = 0
        self.inventory = []
        self.weapon = None
        self.companions = []
        self.status_effects = {}
        self.skill_cooldown = 0
        self.guild = None
        self.race = None
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

    def decrement_cooldowns(self):
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1

    def use_skill(self, enemy):
        if self.skill_cooldown > 0:
            print(f"Your skill is on cooldown for {self.skill_cooldown} more turn(s).")
            return
        if self.class_type == "Warrior":
            damage = self.attack_power * 2
            print(f"You unleash a mighty Power Strike dealing {damage} damage!")
            enemy.take_damage(damage)
        elif self.class_type == "Mage":
            damage = self.attack_power + random.randint(10, 15)
            print(f"You cast Fireball dealing {damage} damage!")
            enemy.take_damage(damage)
            enemy.status_effects = getattr(enemy, 'status_effects', {})
            enemy.status_effects['burn'] = 3
        elif self.class_type == "Rogue":
            damage = self.attack_power + random.randint(5, 10)
            print(f"You perform a sneaky Backstab for {damage} damage!")
            enemy.take_damage(damage)
        else:
            print("You don't have a special skill.")
            return
        if not enemy.is_alive():
            self.process_enemy_defeat(enemy)
        self.skill_cooldown = 3

    def level_up(self):
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
        self.attack_power += 3
        print(f"\nYou leveled up to level {self.level}!")
        print(f"Max Health increased to {self.max_health}")
        print(f"Attack Power increased to {self.attack_power}")
        print(random.choice(ANNOUNCER_LINES))
        if self.level == 3:
            print("You've unlocked Gold Finder: +5 gold after each kill.")
        if self.level == 5:
            print("You've unlocked Passive Regen: Heal 1 HP per move.")

    def join_guild(self, guild):
        self.guild = guild
        if guild == "Warriors' Guild":
            self.max_health += 10
            self.health += 10
        elif guild == "Mages' Guild":
            self.attack_power += 3
        elif guild == "Rogues' Guild":
            self.skill_cooldown = max(0, self.skill_cooldown - 1)
        print(f"You have joined the {guild}!")

    def choose_race(self, race):
        self.race = race
        if race == "Elf":
            self.attack_power += 2
        elif race == "Dwarf":
            self.max_health += 5
            self.health += 5
        elif race == "Orc":
            self.attack_power += 1
            self.max_health += 3
            self.health += 3
        elif race == "Gnome":
            self.max_health += 2
            self.health += 2
        elif race == "Halfling":
            self.skill_cooldown = max(0, self.skill_cooldown - 1)
        elif race == "Catfolk":
            self.attack_power += 1
        elif race == "Lizardfolk":
            self.max_health += 4
            self.health += 4
        print(f"Race selected: {race}.")

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

class Enemy(Entity):
    """Adversary encountered within the dungeon.

    Holds combat statistics and may wield a special ability. The
    :meth:`attack` method applies damage and effects to the player.
    """
    def __init__(self, name, health, attack_power, defense, gold, ability=None):
        super().__init__(name, "")
        self.health = health
        self.attack_power = attack_power
        self.defense = defense
        self.gold = gold
        self.ability = ability
        self.xp = 10
        self.status_effects = {}

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def drop_gold(self):
        return self.gold

    def apply_status_effects(self):
        """Apply ongoing status effects and decrement their duration."""
        skip_turn = False
        if 'poison' in self.status_effects:
            if self.status_effects['poison'] > 0:
                self.health -= 3
                print(f"The {self.name} takes 3 poison damage!")
                self.status_effects['poison'] -= 1
            if self.status_effects['poison'] <= 0:
                del self.status_effects['poison']
        if 'burn' in self.status_effects:
            if self.status_effects['burn'] > 0:
                self.health -= 4
                print(f"The {self.name} suffers 4 burn damage!")
                self.status_effects['burn'] -= 1
            if self.status_effects['burn'] <= 0:
                del self.status_effects['burn']
        if 'freeze' in self.status_effects:
            if self.status_effects['freeze'] > 0:
                print(f"The {self.name} is frozen and can't move!")
                self.status_effects['freeze'] -= 1
                skip_turn = True
            if self.status_effects['freeze'] <= 0:
                del self.status_effects['freeze']
        return skip_turn

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
            print(f"The {self.name} freezes you for 1 turns!")
        elif self.ability == "double_strike" and random.random() < 0.25:
            print(f"The {self.name} strikes twice!")
            player.take_damage(damage)
        player.take_damage(damage)
        print(f"The {self.name} attacked you and dealt {damage} damage.")

class Companion(Entity):
    """NPC ally that grants a minor permanent bonus when recruited."""

    def __init__(self, name, effect):
        super().__init__(name, "A loyal companion")
        self.effect = effect
