"""Game entities such as the player and enemies."""

from __future__ import annotations

import random
from gettext import gettext as _

from .config import config
from .constants import ANNOUNCER_LINES
from .items import Item, Weapon
from .status_effects import add_status_effect
from .status_effects import apply_status_effects as apply_effects


class Entity:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        # Track ongoing status effects shared by all entities
        self.status_effects = {}


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
        self.skill_cooldown = 0
        self.guild = None
        self.race = None
        self.x = 0
        self.y = 0
        self.inventory_limit = 8
        self.cause_of_death = ""
        self.novice_luck_active = False
        self.speed = 10
        # Temporary combat modifiers for the defend action
        self.guard_damage = False
        self.guard_attack = False
        # Start as an untrained crawler. Specific classes can be chosen later
        # via ``choose_class``.
        self.choose_class(class_type, announce=False)
        # Map class names to their respective skill handlers
        self.skill_handlers = {
            "Warrior": self._skill_warrior,
            "Mage": self._skill_mage,
            "Rogue": self._skill_rogue,
            "Cleric": self._skill_cleric,
            "Paladin": self._skill_paladin,
            "Bard": self._skill_bard,
            "Barbarian": self._skill_barbarian,
            "Druid": self._skill_druid,
            "Ranger": self._skill_ranger,
            "Sorcerer": self._skill_sorcerer,
            "Monk": self._skill_monk,
            "Warlock": self._skill_warlock,
            "Necromancer": self._skill_necromancer,
            "Shaman": self._skill_shaman,
            "Alchemist": self._skill_alchemist,
        }

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
            print(_(f"Class selected: {self.class_type}."))

    def is_alive(self):
        return self.health > 0

    def collect_item(self, item):
        if len(self.inventory) >= self.inventory_limit:
            print(
                _(
                    f"Backpack full ({self.inventory_limit}/{self.inventory_limit}). Drop something with [D]."
                )
            )
            return False
        self.inventory.append(item)
        return True

    def has_item(self, name):
        return any(item.name == name for item in self.inventory)

    def use_health_potion(self):
        potion = next(
            (
                item
                for item in self.inventory
                if isinstance(item, Item) and item.name == "Health Potion"
            ),
            None,
        )
        if potion:
            self.inventory.remove(potion)
            healed_amount = min(20, self.max_health - self.health)
            self.health += healed_amount
            print(_(f"You used a Health Potion and gained {healed_amount} health."))
        else:
            print(_("You don't have a Health Potion to use."))

    def flee(self, enemy: "Enemy") -> bool:
        """Attempt to flee from ``enemy``.

        Returns ``True`` if the escape succeeds. Otherwise the enemy gains
        advantage on their next attack.
        """

        base_chance = 40 + (self.speed - enemy.speed) * 5
        escape_chance = max(10, min(90, base_chance))
        roll = random.randint(1, 100)
        if roll <= escape_chance:
            print(_("You successfully disengage!"))
            return True
        print(
            _(f"You try to disengage, but the {enemy.name} pins you (they gain advantage!).")
        )
        enemy.status_effects["advantage"] = 1
        return False

    def attack(self, enemy: Enemy) -> None:
        """Attack ``enemy`` using the equipped weapon or base attack power.

        Applies any weapon effects and awards experience and gold if the enemy
        is defeated.
        """
        hit_chance = 85
        if self.guard_attack:
            hit_chance += 10
            # Guard bonus consumed once you swing
            self.guard_attack = False
            self.status_effects.pop("guard", None)
        if getattr(self, "novice_luck_active", False):
            hit_chance += 10
        roll = random.randint(1, 100)
        base = self.calculate_damage()
        str_bonus = 0
        damage = base + str_bonus
        if roll <= hit_chance:
            self.apply_weapon_effect(enemy)
            enemy.take_damage(damage)
            if config.verbose_combat:
                print(
                    _(
                        f"You swing ({hit_chance}% to hit): roll {roll} → HIT. Damage {damage} ({base} base +{str_bonus} STR)."
                    )
                )
            else:
                print(_(f"You hit the {enemy.name} for {damage} damage."))
            if not enemy.is_alive():
                self.process_enemy_defeat(enemy)
        else:
            if config.verbose_combat:
                reason = "It slipped on the wet stone!"
                print(
                    _(f"You swing ({hit_chance}% to hit): roll {roll} → MISS. {reason}")
                )
            else:
                print(_(f"You missed the {enemy.name}."))

    def calculate_damage(self) -> int:
        """Return the damage dealt by the player's current attack."""
        if self.weapon:
            return random.randint(self.weapon.min_damage, self.weapon.max_damage)
        return random.randint(self.attack_power // 2, self.attack_power)

    def apply_weapon_effect(self, enemy: Enemy) -> None:
        """Apply the equipped weapon's status effect to ``enemy`` if present."""
        if self.weapon and getattr(self.weapon, "effect", None):
            add_status_effect(enemy, self.weapon.effect, 3)

    def process_enemy_defeat(self, enemy: Enemy) -> None:
        """Handle rewards for defeating ``enemy`` such as XP and gold."""
        self.xp += enemy.xp
        gold_dropped = enemy.drop_gold()
        if self.level >= 3:
            gold_dropped += 5
        self.gold += gold_dropped
        print(_(f"You defeated the {enemy.name}!"))
        print(_(f"You gained {enemy.xp} XP and {gold_dropped} gold."))
        while self.xp >= self.level * 20:
            self.xp -= self.level * 20
            self.level_up()

    def defend(self, enemy=None):
        """Prepare to mitigate the next blow and steady the next strike."""

        self.guard_damage = True
        self.guard_attack = True
        self.status_effects["guard"] = 1
        print(
            _(
                "You brace yourself. Incoming damage -40% next hit; your next strike steadies (+10% hit)."
            )
        )

    def take_damage(self, damage, source=None):
        if self.guard_damage:
            damage = int(damage * 0.6)
            self.guard_damage = False
        if "shield" in self.status_effects:
            damage = max(0, damage - 5)
            print(_("Your shield absorbs 5 damage!"))
        if getattr(self, "novice_luck_active", False):
            damage = max(0, damage - 1)
        self.health = max(0, self.health - damage)
        if self.health <= 0:
            self.cause_of_death = source or "unknown"

    def apply_status_effects(self):
        """Delegate to the shared status effect helper."""
        return apply_effects(self)

    def decrement_cooldowns(self):
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1

    # Skill handler implementations
    def _skill_warrior(self, enemy):
        damage = self.attack_power * 2
        print(_(f"You unleash a mighty Power Strike dealing {damage} damage!"))
        enemy.take_damage(damage)

    def _skill_mage(self, enemy):
        damage = self.attack_power + random.randint(10, 15)
        print(_(f"You cast Fireball dealing {damage} damage!"))
        enemy.take_damage(damage)
        add_status_effect(enemy, "burn", 3)

    def _skill_rogue(self, enemy):
        damage = self.attack_power + random.randint(5, 10)
        print(_(f"You perform a sneaky Backstab for {damage} damage!"))
        enemy.take_damage(damage)

    def _skill_cleric(self, enemy):
        heal = min(20, self.max_health - self.health)
        self.health += heal
        print(_(f"You invoke Healing Light and recover {heal} health!"))

    def _skill_paladin(self, enemy):
        damage = self.attack_power + random.randint(5, 12)
        print(_(f"You smite the {enemy.name} for {damage} holy damage!"))
        enemy.take_damage(damage)
        heal = min(10, self.max_health - self.health)
        if heal:
            self.health += heal
            print(_(f"Divine power heals you for {heal} HP!"))

    def _skill_bard(self, enemy):
        print(_("You play an inspiring tune, bolstering your spirit!"))
        add_status_effect(self, "inspire", 3)

    def _skill_barbarian(self, enemy):
        damage = self.attack_power + random.randint(8, 12)
        enemy.take_damage(damage)
        heal = min(10, self.max_health - self.health)
        self.health += heal
        print(_(f"You enter a rage, dealing {damage} damage and healing {heal}!"))

    def _skill_druid(self, enemy):
        damage = self.attack_power + random.randint(5, 10)
        enemy.take_damage(damage)
        add_status_effect(enemy, "freeze", 1)
        heal = min(5, self.max_health - self.health)
        self.health += heal
        print(_(f"Nature's wrath deals {damage} damage and restores {heal} health!"))

    def _skill_ranger(self, enemy):
        damage = self.attack_power + random.randint(6, 12)
        enemy.take_damage(damage)
        add_status_effect(enemy, "poison", 3)
        print(_(f"A volley of arrows hits for {damage} damage and poisons the foe!"))

    def _skill_sorcerer(self, enemy):
        damage = self.attack_power + random.randint(12, 18)
        enemy.take_damage(damage)
        add_status_effect(enemy, "burn", 3)
        print(_(f"You unleash Arcane Blast for {damage} damage!"))

    def _skill_monk(self, enemy):
        damage = self.attack_power + random.randint(4, 8)
        enemy.take_damage(damage)
        enemy.take_damage(damage)
        print(_(f"You strike twice with a flurry for {damage * 2} total damage!"))

    def _skill_warlock(self, enemy):
        damage = self.attack_power + random.randint(8, 12)
        enemy.take_damage(damage)
        heal = min(damage // 2, self.max_health - self.health)
        self.health += heal
        print(_(f"Eldritch energy deals {damage} damage and heals you for {heal}!"))

    def _skill_necromancer(self, enemy):
        damage = self.attack_power + random.randint(5, 10)
        enemy.take_damage(damage)
        heal = min(damage // 2, self.max_health - self.health)
        self.health += heal
        print(_(f"You siphon the enemy's soul for {damage} damage and {heal} health!"))

    def _skill_shaman(self, enemy):
        heal = min(15, self.max_health - self.health)
        self.health += heal
        damage = self.attack_power + random.randint(4, 8)
        enemy.take_damage(damage)
        print(_(f"Spirits mend you for {heal} and shock the foe for {damage} damage!"))

    def _skill_alchemist(self, enemy):
        damage = self.attack_power + random.randint(8, 12)
        enemy.take_damage(damage)
        add_status_effect(enemy, "burn", 3)
        print(
            _(f"An explosive flask bursts for {damage} damage and sets the foe ablaze!")
        )

    def use_skill(self, enemy):
        if self.skill_cooldown > 0:
            print(
                _(f"Your skill is on cooldown for {self.skill_cooldown} more turn(s).")
            )
            return
        handler = self.skill_handlers.get(self.class_type)
        if not handler:
            print(_("You don't have a special skill."))
            return
        handler(enemy)
        if not enemy.is_alive():
            self.process_enemy_defeat(enemy)
        self.skill_cooldown = 3

    def level_up(self):
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
        self.attack_power += 3
        print(_(f"\nYou leveled up to level {self.level}!"))
        print(_(f"Max Health increased to {self.max_health}"))
        print(_(f"Attack Power increased to {self.attack_power}"))
        print(random.choice(ANNOUNCER_LINES))
        if self.level == 3:
            print(_("You've unlocked Gold Finder: +5 gold after each kill."))
        if self.level == 5:
            print(_("You've unlocked Passive Regen: Heal 1 HP per move."))

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
        print(_(f"You have joined the {guild}!"))

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
        print(_(f"Race selected: {race}."))

    def equip_weapon(self, weapon):
        if weapon in self.inventory and isinstance(weapon, Weapon):
            if self.weapon:
                self.inventory.append(self.weapon)
                print(_(f"You unequipped the {self.weapon.name}"))
            self.weapon = weapon
            self.inventory.remove(weapon)
            print(_(f"You equipped the {weapon.name}"))
        else:
            print(_("You don't have a valid weapon to equip."))

    def get_score(self):
        return self.level * 100 + len(self.inventory) * 10 + self.gold


class Enemy(Entity):
    """Adversary encountered within the dungeon.

    Holds combat statistics and may wield a special ability. The
    :meth:`attack` method applies damage and effects to the player.
    """

    def __init__(
        self,
        name,
        health,
        attack_power,
        defense,
        gold,
        ability=None,
        ai=None,
        speed=10,
    ):
        super().__init__(name, "")
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.defense = defense
        self.gold = gold
        self.ability = ability
        self.ai = ai
        self.xp = 10
        self.speed = speed

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        if "shield" in self.status_effects:
            damage = max(0, damage - 5)
            print(_(f"The {self.name}'s shield absorbs 5 damage!"))
        self.health = max(0, self.health - damage)

    def drop_gold(self):
        return self.gold

    def apply_status_effects(self):
        """Delegate to the shared status effect helper."""
        return apply_effects(self)

    def defend(self):
        add_status_effect(self, "shield", 1)
        print(_(f"The {self.name} raises its guard!"))

    def take_turn(self, player):
        action = "attack"
        if self.ai:
            action = self.ai.choose_action(self, player)
        if action == "defend":
            self.defend()
        else:
            self.attack(player)

    def attack(self, player):
        hit_chance = 60
        if self.status_effects.pop("advantage", 0):
            hit_chance += 15
        roll = random.randint(1, 100)
        damage = random.randint(self.attack_power // 2, self.attack_power)
        if roll <= hit_chance:
            if self.ability == "lifesteal":
                self.health += damage // 3
                print(_(f"The {self.name} drains life and heals for {damage // 3}!"))
            elif self.ability == "poison":
                add_status_effect(player, "poison", 3)
            elif self.ability == "burn":
                add_status_effect(player, "burn", 3)
            elif self.ability == "stun":
                add_status_effect(player, "stun", 1)
            elif self.ability == "bleed":
                add_status_effect(player, "bleed", 3)
            elif self.ability == "freeze":
                add_status_effect(player, "freeze", 1)
            elif self.ability == "double_strike" and random.random() < 0.25:
                print(_(f"The {self.name} strikes twice!"))
                player.take_damage(damage, source=self.name)
            player.take_damage(damage, source=self.name)
            if config.verbose_combat:
                print(
                    _(
                        f"{self.name} attacks ({hit_chance}%): roll {roll} → HIT. Damage {damage}."
                    )
                )
            else:
                print(_(f"The {self.name} attacked you and dealt {damage} damage."))
        else:
            if config.verbose_combat:
                reason = "It slipped on the wet stone!"
                print(
                    _(
                        f"{self.name} attacks ({hit_chance}%): roll {roll} → MISS. {reason}"
                    )
                )
            else:
                print(_(f"The {self.name}'s attack missed."))


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
            print(_(f"{self.name} strikes {enemy.name} for {dmg} damage!"))
        if self.heal_amount and player.is_alive():
            heal = min(self.heal_amount, player.max_health - player.health)
            if heal > 0:
                player.health += heal
                print(_(f"{self.name} heals {player.name} for {heal} HP!"))
