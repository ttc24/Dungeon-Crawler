"""Game entities such as the player and enemies."""

from __future__ import annotations

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
    :meth:`level_up`, :meth:`join_guild`, :meth:`choose_race` and
    :meth:`choose_class`.
    """

    def __init__(self, name, class_type="Novice"):
        super().__init__(name, "The player")
        self.level = 1
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
        # Start as an untrained crawler. Specific classes can be chosen later
        # via ``choose_class``.
        self.choose_class(class_type, announce=False)

    def choose_class(self, class_type, announce=True):
        """Select a class and update core stats accordingly.

        A large selection of classes is available, each inspired by the
        Dungeon Crawl Classics canon and providing its own stat profile.
        """

        self.class_type = class_type
        stats = {
            "Mage": (80, 14),
            "Rogue": (90, 12),
            "Cleric": (110, 9),
            "Paladin": (120, 11),
            "Bard": (90, 10),
            "Warrior": (100, 10),
            # New classes inspired by the tabletop source material
            "Barbarian": (130, 12),
            "Druid": (105, 11),
            "Ranger": (105, 11),
            "Sorcerer": (85, 15),
            "Monk": (95, 11),
            "Warlock": (85, 14),
            "Necromancer": (90, 13),
            "Shaman": (100, 12),
            "Alchemist": (95, 12),
        }

        if class_type not in stats:
            self.class_type = "Novice"
            self.max_health = 100
            self.attack_power = 10
        else:
            self.max_health, self.attack_power = stats[class_type]

        self.health = self.max_health
        if announce:
            print(f"Class selected: {self.class_type}.")

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

    def attack(self, enemy: Enemy) -> None:
        """Attack ``enemy`` using the equipped weapon or base attack power.

        Applies any weapon effects and awards experience and gold if the enemy
        is defeated.
        """
        damage: int = self.calculate_damage()
        self.apply_weapon_effect(enemy)
        print(f"You attacked the {enemy.name} and dealt {damage} damage!")
        enemy.take_damage(damage)
        if not enemy.is_alive():
            self.process_enemy_defeat(enemy)

    def calculate_damage(self) -> int:
        """Return the damage dealt by the player's current attack."""
        if self.weapon:
            return random.randint(self.weapon.min_damage, self.weapon.max_damage)
        return random.randint(self.attack_power // 2, self.attack_power)

    def apply_weapon_effect(self, enemy: Enemy) -> None:
        """Apply the equipped weapon's status effect to ``enemy`` if present."""
        if self.weapon and hasattr(self.weapon, "effect") and self.weapon.effect:
            effect = self.weapon.effect
            enemy.status_effects = getattr(enemy, "status_effects", {})
            enemy.status_effects[effect] = 3
            print(f"Your weapon inflicts {effect} on the {enemy.name}!")

    def process_enemy_defeat(self, enemy: Enemy) -> None:
        """Handle rewards for defeating ``enemy`` such as XP and gold."""
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
        if 'shield' in self.status_effects:
            damage = max(0, damage - 5)
            print("Your shield absorbs 5 damage!")
        self.health = max(0, self.health - damage)

    def apply_status_effects(self):
        skip_turn = False
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
        if 'bleed' in self.status_effects:
            bleed_turns = self.status_effects['bleed']
            if bleed_turns > 0:
                self.health -= 2
                print("You bleed for 2 damage!")
                self.status_effects['bleed'] -= 1
            if self.status_effects['bleed'] <= 0:
                del self.status_effects['bleed']
        if 'freeze' in self.status_effects:
            freeze_turns = self.status_effects['freeze']
            if freeze_turns > 0:
                print("You're frozen and lose your turn!")
                self.status_effects['freeze'] -= 1
                skip_turn = True
            if self.status_effects['freeze'] <= 0:
                del self.status_effects['freeze']
        if 'stun' in self.status_effects:
            stun_turns = self.status_effects['stun']
            if stun_turns > 0:
                print("You're stunned and can't move!")
                self.status_effects['stun'] -= 1
                skip_turn = True
            if self.status_effects['stun'] <= 0:
                del self.status_effects['stun']
        if 'shield' in self.status_effects:
            self.status_effects['shield'] -= 1
            if self.status_effects['shield'] <= 0:
                print("Your shield fades.")
                del self.status_effects['shield']
        if 'inspire' in self.status_effects:
            if self.status_effects['inspire'] == 3:
                self.attack_power += 3
            self.status_effects['inspire'] -= 1
            if self.status_effects['inspire'] <= 0:
                self.attack_power -= 3
                del self.status_effects['inspire']
        return skip_turn

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
        elif self.class_type == "Cleric":
            heal = min(20, self.max_health - self.health)
            self.health += heal
            print(f"You invoke Healing Light and recover {heal} health!")
        elif self.class_type == "Paladin":
            damage = self.attack_power + random.randint(5, 12)
            print(f"You smite the {enemy.name} for {damage} holy damage!")
            enemy.take_damage(damage)
            heal = min(10, self.max_health - self.health)
            if heal:
                self.health += heal
                print(f"Divine power heals you for {heal} HP!")
        elif self.class_type == "Bard":
            print("You play an inspiring tune, bolstering your spirit!")
            self.status_effects['inspire'] = 3
        elif self.class_type == "Barbarian":
            damage = self.attack_power + random.randint(8, 12)
            enemy.take_damage(damage)
            heal = min(10, self.max_health - self.health)
            self.health += heal
            print(f"You enter a rage, dealing {damage} damage and healing {heal}!")
        elif self.class_type == "Druid":
            damage = self.attack_power + random.randint(5, 10)
            enemy.take_damage(damage)
            enemy.status_effects['freeze'] = 1
            heal = min(5, self.max_health - self.health)
            self.health += heal
            print(f"Nature's wrath deals {damage} damage and restores {heal} health!")
        elif self.class_type == "Ranger":
            damage = self.attack_power + random.randint(6, 12)
            enemy.take_damage(damage)
            enemy.status_effects['poison'] = 3
            print(f"A volley of arrows hits for {damage} damage and poisons the foe!")
        elif self.class_type == "Sorcerer":
            damage = self.attack_power + random.randint(12, 18)
            enemy.take_damage(damage)
            enemy.status_effects['burn'] = 3
            print(f"You unleash Arcane Blast for {damage} damage!")
        elif self.class_type == "Monk":
            damage = self.attack_power + random.randint(4, 8)
            enemy.take_damage(damage)
            enemy.take_damage(damage)
            print(f"You strike twice with a flurry for {damage * 2} total damage!")
        elif self.class_type == "Warlock":
            damage = self.attack_power + random.randint(8, 12)
            enemy.take_damage(damage)
            heal = min(damage // 2, self.max_health - self.health)
            self.health += heal
            print(f"Eldritch energy deals {damage} damage and heals you for {heal}!")
        elif self.class_type == "Necromancer":
            damage = self.attack_power + random.randint(5, 10)
            enemy.take_damage(damage)
            heal = min(damage // 2, self.max_health - self.health)
            self.health += heal
            print(f"You siphon the enemy's soul for {damage} damage and {heal} health!")
        elif self.class_type == "Shaman":
            heal = min(15, self.max_health - self.health)
            self.health += heal
            damage = self.attack_power + random.randint(4, 8)
            enemy.take_damage(damage)
            print(f"Spirits mend you for {heal} and shock the foe for {damage} damage!")
        elif self.class_type == "Alchemist":
            damage = self.attack_power + random.randint(8, 12)
            enemy.take_damage(damage)
            enemy.status_effects['burn'] = 3
            print(f"An explosive flask bursts for {damage} damage and sets the foe ablaze!")
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
        elif guild == "Healers' Circle":
            self.max_health += 8
            self.health += 8
        elif guild == "Shadow Brotherhood":
            self.attack_power += 4
        elif guild == "Arcane Order":
            self.attack_power += 2
            self.skill_cooldown = max(0, self.skill_cooldown - 1)
        elif guild == "Rangers' Lodge":
            self.max_health += 5
            self.health += 5
            self.attack_power += 1
        elif guild == "Berserkers' Clan":
            self.attack_power += 3
        print(f"You have joined the {guild}!")

    def choose_race(self, race):
        self.race = race
        if race == "Human":
            self.max_health += 1
            self.health += 1
            self.attack_power += 1
        elif race == "Elf":
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
        elif race == "Tiefling":
            self.attack_power += 2
        elif race == "Aasimar":
            self.max_health += 4
            self.health += 4
        elif race == "Goblin":
            self.skill_cooldown = max(0, self.skill_cooldown - 1)
        elif race == "Dragonborn":
            self.attack_power += 2
            self.max_health += 2
            self.health += 2
        elif race == "Half-Elf":
            self.attack_power += 1
            self.max_health += 2
            self.health += 2
        elif race == "Kobold":
            self.attack_power += 1
        elif race == "Triton":
            self.max_health += 3
            self.health += 3
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

    def __init__(self, name, health, attack_power, defense, gold, ability=None, ai=None):
        super().__init__(name, "")
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.defense = defense
        self.gold = gold
        self.ability = ability
        self.ai = ai
        self.xp = 10
        self.status_effects = {}

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        if 'shield' in self.status_effects:
            damage = max(0, damage - 5)
            print(f"The {self.name}'s shield absorbs 5 damage!")
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
        if 'bleed' in self.status_effects:
            if self.status_effects['bleed'] > 0:
                self.health -= 2
                print(f"The {self.name} bleeds for 2 damage!")
                self.status_effects['bleed'] -= 1
            if self.status_effects['bleed'] <= 0:
                del self.status_effects['bleed']
        if 'freeze' in self.status_effects:
            if self.status_effects['freeze'] > 0:
                print(f"The {self.name} is frozen and can't move!")
                self.status_effects['freeze'] -= 1
                skip_turn = True
            if self.status_effects['freeze'] <= 0:
                del self.status_effects['freeze']
        if 'stun' in self.status_effects:
            if self.status_effects['stun'] > 0:
                print(f"The {self.name} is stunned and can't move!")
                self.status_effects['stun'] -= 1
                skip_turn = True
            if self.status_effects['stun'] <= 0:
                del self.status_effects['stun']
        if 'shield' in self.status_effects:
            self.status_effects['shield'] -= 1
            if self.status_effects['shield'] <= 0:
                print(f"The {self.name}'s shield fades.")
                del self.status_effects['shield']
        return skip_turn

    def defend(self):
        self.status_effects['shield'] = 1
        print(f"The {self.name} raises its guard!")

    def take_turn(self, player):
        action = 'attack'
        if self.ai:
            action = self.ai.choose_action(self, player)
        if action == 'defend':
            self.defend()
        else:
            self.attack(player)

    def attack(self, player):
        damage = random.randint(self.attack_power // 2, self.attack_power)
        if self.ability == "lifesteal":
            self.health += damage // 3
            print(f"The {self.name} drains life and heals for {damage // 3}!")
        elif self.ability == "poison":
            player.status_effects['poison'] = 3
        elif self.ability == "burn":
            player.status_effects['burn'] = 3
        elif self.ability == "stun":
            player.status_effects['stun'] = 1
            print(f"The {self.name} stuns you!")
        elif self.ability == "bleed":
            player.status_effects['bleed'] = 3
        elif self.ability == "freeze":
            player.status_effects['freeze'] = 1
            print(f"The {self.name} freezes you for 1 turns!")
        elif self.ability == "double_strike" and random.random() < 0.25:
            print(f"The {self.name} strikes twice!")
            player.take_damage(damage)
        player.take_damage(damage)
        print(f"The {self.name} attacked you and dealt {damage} damage.")

class Companion(Entity):
    """NPC ally that can aid the player during combat.

    Companions may be offensive or supportive.  Attack-oriented
    companions deal a small amount of damage to the enemy each round,
    while healer companions restore a bit of the player's health.  The
    previously existing ``effect`` attribute remains for future use
    (e.g. passive bonuses) but is optional.
    """

    def __init__(self, name, effect=None, attack_power=0, heal_amount=0):
        super().__init__(name, "A loyal companion")
        self.effect = effect
        self.attack_power = attack_power
        self.heal_amount = heal_amount

    def assist(self, player, enemy):
        """Perform the companion's action for the round.

        Parameters
        ----------
        player : :class:`Player`
            The player being assisted.
        enemy : :class:`Enemy`
            The current enemy, if any.
        """

        if self.attack_power and enemy.is_alive():
            dmg = random.randint(max(1, self.attack_power // 2), self.attack_power)
            enemy.take_damage(dmg)
            print(f"{self.name} strikes {enemy.name} for {dmg} damage!")
        if self.heal_amount and player.is_alive():
            heal = min(self.heal_amount, player.max_health - player.health)
            if heal > 0:
                player.health += heal
                print(f"{self.name} heals {player.name} for {heal} HP!")
