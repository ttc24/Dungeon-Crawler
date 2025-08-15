"""Game entities such as the player and enemies."""

from __future__ import annotations

import json
import random
from functools import lru_cache
from gettext import gettext as _
from pathlib import Path

from .config import config
from .constants import ANNOUNCER_LINES
from .items import RARITY_MODIFIERS, Armor, Item, Trinket, Weapon
from .status_effects import add_status_effect
from .status_effects import apply_status_effects as apply_effects

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=None)
def load_skills():
    path = DATA_DIR / "skills.json"
    with open(path) as f:
        return json.load(f)


SKILL_DEFS = load_skills()


# Definitions for player classes, guilds and races. Each class includes a
# stat block and optional abilities with stamina costs. Guild and race
# dictionaries specify permanent bonuses applied when joined or selected.

CLASS_DEFS = {
    "Warrior": {
        "stats": {"max_health": 100, "attack_power": 10},
        "abilities": {"Shield Slam": {"cost": 25, "description": "Briefly stun a foe."}},
    },
    "Mage": {
        "stats": {"max_health": 80, "attack_power": 14},
        "abilities": {"Arcane Bolt": {"cost": 30, "description": "Ranged magical attack."}},
    },
    "Rogue": {
        "stats": {"max_health": 90, "attack_power": 12},
        "abilities": {"Backstab": {"cost": 20, "description": "High damage from stealth."}},
    },
    "Cleric": {
        "stats": {"max_health": 110, "attack_power": 9},
        "abilities": {"Heal": {"cost": 25, "description": "Restore a small amount of HP."}},
    },
    "Barbarian": {
        "stats": {"max_health": 130, "attack_power": 12},
        "abilities": {
            "Rage": {"cost": 30, "description": "Boost attack for one turn."},
            "Whirlwind": {
                "cost": 40,
                "description": "Strike all adjacent enemies.",
            },
        },
    },
    "Ranger": {
        "stats": {"max_health": 105, "attack_power": 11},
        "abilities": {"Snipe": {"cost": 20, "description": "Long-range shot."}},
    },
    "Druid": {
        "stats": {"max_health": 100, "attack_power": 11},
        "abilities": {
            "Wild Shape": {
                "cost": 35,
                "description": "Transform to beast and gain HP.",
            },
            "Entangle": {
                "cost": 20,
                "description": "Roots an enemy in place.",
            },
        },
    },
    "Sorcerer": {
        "stats": {"max_health": 75, "attack_power": 15},
        "abilities": {"Chain Lightning": {"cost": 35, "description": "Hit multiple foes."}},
    },
    "Monk": {
        "stats": {"max_health": 95, "attack_power": 13},
        "abilities": {"Flurry": {"cost": 25, "description": "Series of rapid strikes."}},
    },
    "Warlock": {
        "stats": {"max_health": 85, "attack_power": 14},
        "abilities": {"Eldritch Blast": {"cost": 30, "description": "Beam of dark power."}},
    },
    "Necromancer": {
        "stats": {"max_health": 90, "attack_power": 13},
        "abilities": {
            "Raise Skeleton": {
                "cost": 40,
                "description": "Summon a skeletal ally.",
            }
        },
    },
    "Shaman": {
        "stats": {"max_health": 110, "attack_power": 10},
        "abilities": {"Spirit Call": {"cost": 30, "description": "Invoke ancestral aid."}},
    },
    "Alchemist": {
        "stats": {"max_health": 90, "attack_power": 12},
        "abilities": {"Acid Flask": {"cost": 25, "description": "Splash corrosive acid."}},
    },
}

GUILD_DEFS = {
    "Warriors' Guild": {
        "max_health": 10,
        "perks": ["+10 max health"],
        "skill": {
            "name": "Warrior Technique",
            "cost": 20,
            "base_cooldown": 4,
            "func": "guild_skill",
        },
    },
    "Mages' Guild": {
        "attack_power": 3,
        "perks": ["+3 attack power"],
        "skill": {
            "name": "Mage Technique",
            "cost": 20,
            "base_cooldown": 4,
            "func": "guild_skill",
        },
    },
    "Rogues' Guild": {
        "cooldown_reduction": 1,
        "perks": ["-1 cooldown to all skills"],
        "skill": {
            "name": "Rogue Technique",
            "cost": 20,
            "base_cooldown": 4,
            "func": "guild_skill",
        },
    },
    "Healers' Circle": {
        "max_health": 8,
        "perks": ["+8 max health"],
        "skill": {
            "name": "Healer Technique",
            "cost": 20,
            "base_cooldown": 4,
            "func": "guild_skill",
        },
    },
    "Shadow Brotherhood": {
        "attack_power": 4,
        "skill_cost_reduction": 5,
        "perks": ["+4 attack power", "Skills cost 5 less stamina"],
        "skill": {
            "name": "Shadow Technique",
            "cost": 20,
            "base_cooldown": 4,
            "func": "guild_skill",
        },
    },
    "Arcane Order": {
        "attack_power": 2,
        "perks": ["+2 attack power"],
        "skill": {
            "name": "Arcane Technique",
            "cost": 20,
            "base_cooldown": 4,
            "func": "guild_skill",
        },
    },
}

RACE_DEFS = {
    "Human": {
        "max_health": 1,
        "attack_power": 1,
        "traits": ["Jack of all trades"],
    },
    "Elf": {"attack_power": 2, "traits": ["Keen senses"]},
    "Dwarf": {"max_health": 5, "traits": ["Stonecunning"]},
    "Orc": {
        "max_health": 3,
        "attack_power": 1,
        "traits": ["Savage strength"],
    },
    "Gnome": {"max_health": 2, "traits": ["Trickster"]},
    "Tiefling": {"attack_power": 2, "traits": ["Infernal resistance"]},
    "Dragonborn": {
        "max_health": 2,
        "attack_power": 2,
        "traits": ["Draconic breath"],
    },
    "Goblin": {"attack_power": 1, "traits": ["Sneaky"]},
}


class Entity:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        # Track ongoing status effects shared by all entities
        self.status_effects = {}
        # Equipment slots
        self.weapon: Weapon | None = None
        self.armor: Armor | None = None
        self.trinket: Trinket | None = None
        # Rarity influences damage and effects
        self.rarity = "common"


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
        self.credits = 0
        self.inventory = []
        self.companions = []
        self.guild = None
        self.guild_perks = []
        self.race = None
        self.racial_traits = []
        # Record collected lore notes
        self.codex = []
        # Stamina based skill system
        self.max_stamina = 100
        self.stamina = 100
        self.skills = {}
        for cfg in SKILL_DEFS:
            key = cfg["key"]
            func = getattr(self, f"_skill_{cfg['func']}")
            self.skills[key] = {
                "name": cfg["name"],
                "cost": cfg["cost"],
                "base_cooldown": cfg["base_cooldown"],
                "cooldown": 0,
                "func": func,
            }
        self.class_abilities = {}
        self.x = 0
        self.y = 0
        self.inventory_limit = 8
        self.cause_of_death = ""
        self.novice_luck_active = False
        self.speed = 10
        self.vision = 5
        self.heal_multiplier = 1.0
        # Temporary combat modifiers for the defend action
        self.guard_damage = False
        self.guard_attack = False
        # Floor-scoped temporary buffs
        self.temp_strength = 0
        self.temp_intelligence = 0
        # Start as an untrained crawler. Specific classes can be chosen later
        # via ``choose_class``.
        self.choose_class(class_type, announce=False)

    def choose_class(self, class_type, announce=True):
        """Select a class and update core stats accordingly.

        A large selection of classes is available, each inspired by the
        Dungeon Crawl Classics canon and providing its own stat profile.
        """

        self.class_type = class_type
        cls = CLASS_DEFS.get(class_type)
        if not cls:
            self.class_type = "Novice"
            self.max_health = 100
            self.attack_power = 10
            self.class_abilities = {}
        else:
            stats = cls.get("stats", {})
            self.max_health = stats.get("max_health", 100)
            self.attack_power = stats.get("attack_power", 10)
            self.class_abilities = cls.get("abilities", {})

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

    def heal(self, amount: int) -> int:
        """Restore ``amount`` health adjusted by ``heal_multiplier``."""

        amount = int(amount * getattr(self, "heal_multiplier", 1))
        healed = min(amount, self.max_health - self.health)
        if healed > 0:
            self.health += healed
        return healed

    def use_health_potion(self):
        potion = None
        heal = 0
        for item in self.inventory:
            if isinstance(item, Item) and item.name == "Health Potion":
                potion = item
                heal = 20
                break
            if isinstance(item, Item) and item.name == "Fountain Water":
                potion = item
                heal = random.randint(4, 6)
                break
        if potion:
            self.inventory.remove(potion)
            healed_amount = self.heal(heal)
            print(_(f"You used a {potion.name} and gained {healed_amount} health."))
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
        print(_(f"You try to disengage, but the {enemy.name} pins you (they gain advantage!)."))
        enemy.status_effects["advantage"] = 1
        return False

    def attack(self, enemy: Enemy) -> None:
        """Attack ``enemy`` using the equipped weapon or base attack power.

        Applies any weapon effects and awards experience and credits if the enemy
        is defeated.
        """
        hit_chance = 85
        if self.guard_attack:
            hit_chance += 10
            # Guard bonus consumed once you swing
            self.guard_attack = False
            self.status_effects.pop("guard", None)
            print(_("Your steady stance improves your aim (+10% hit)."))
        if getattr(self, "novice_luck_active", False):
            hit_chance += 10
        if "blessed" in self.status_effects:
            hit_chance += 10
        if "cursed" in self.status_effects:
            hit_chance -= 5
        if "beetle_bane" in self.status_effects and "beetle" in enemy.name.lower():
            hit_chance += 5
        roll = random.randint(1, 100)
        base = self.calculate_damage()
        str_bonus = getattr(self, "temp_strength", 0)
        damage = base + str_bonus
        # Treat a maximum roll as an automatic hit so tests that patch
        # ``random.randint`` to always return the upper bound don't end up in
        # an endless loop where the player perpetually misses.
        if roll == 100 or roll <= hit_chance:
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
                print(_(f"You swing ({hit_chance}% to hit): roll {roll} → MISS. {reason}"))
            else:
                print(_(f"You missed the {enemy.name}."))

    def calculate_damage(self) -> int:
        """Return the damage dealt by the player's current attack."""
        if self.weapon:
            base = random.randint(self.weapon.min_damage, self.weapon.max_damage)
            return int(base * RARITY_MODIFIERS.get(self.weapon.rarity, 1.0))
        base = random.randint(self.attack_power // 2, self.attack_power)
        return int(base * RARITY_MODIFIERS.get(self.rarity, 1.0))

    def apply_weapon_effect(self, enemy: Enemy) -> None:
        """Apply equipped item effects to ``enemy`` if present."""
        if self.weapon:
            effect = getattr(self.weapon, "effect", None)
            if effect:
                duration = int(3 * RARITY_MODIFIERS.get(self.weapon.rarity, 1.0))
                add_status_effect(enemy, effect, duration)
        if self.trinket:
            effect = getattr(self.trinket, "effect", None)
            if effect:
                duration = int(2 * RARITY_MODIFIERS.get(self.trinket.rarity, 1.0))
                add_status_effect(enemy, effect, duration)

    def process_enemy_defeat(self, enemy: Enemy) -> None:
        """Handle rewards for defeating ``enemy`` such as XP and credits."""
        self.xp += enemy.xp
        credits_dropped = enemy.drop_credits()
        if self.level >= 3:
            credits_dropped += 5
        self.credits += credits_dropped
        print(_(f"You defeated the {enemy.name}!"))
        print(_(f"You gained {enemy.xp} XP and {credits_dropped} credits."))
        while self.xp >= self.level * 20:
            self.xp -= self.level * 20
            self.level_up()

    def defend(self, enemy=None):
        """Prepare to mitigate the next blow and steady the next strike."""

        self.guard_damage = True
        self.guard_attack = True
        self.status_effects["guard"] = 1
        print(_("You brace yourself. Incoming damage reduced."))

    def take_damage(self, damage, source=None):
        if self.guard_damage:
            damage = int(damage * 0.6)
            self.guard_damage = False
        if "shield" in self.status_effects:
            damage = max(0, damage - 5)
            print(_("Your shield absorbs 5 damage!"))
        if self.armor:
            damage = max(0, damage - self.armor.defense)
            damage = int(damage / RARITY_MODIFIERS.get(self.armor.rarity, 1.0))
            effect = getattr(self.armor, "effect", None)
            if effect:
                duration = int(2 * RARITY_MODIFIERS.get(self.armor.rarity, 1.0))
                add_status_effect(self, effect, duration)
        if getattr(self, "novice_luck_active", False):
            damage = max(0, damage - 1)
        self.health = max(0, self.health - damage)
        if self.health <= 0:
            self.cause_of_death = source or "unknown"

    def apply_status_effects(self):
        """Delegate to the shared status effect helper."""
        return apply_effects(self)

    def decrement_cooldowns(self):
        for skill in self.skills.values():
            if skill["cooldown"] > 0:
                skill["cooldown"] -= 1

    # Light-weight skill implementations
    def _skill_power_strike(self, enemy):
        hit_chance = 75
        roll = random.randint(1, 100)
        base = self.calculate_damage()
        damage = int(base * 1.5)
        if roll <= hit_chance:
            self.apply_weapon_effect(enemy)
            enemy.take_damage(damage)
            print(_(f"Power Strike hits for {damage} damage!"))
            if not enemy.is_alive():
                self.process_enemy_defeat(enemy)
        else:
            print(_("Power Strike misses."))

    def _skill_feint(self, enemy):
        hit_chance = 85
        roll = random.randint(1, 100)
        base = self.calculate_damage()
        damage = int(base * 0.5)
        if roll <= hit_chance:
            self.apply_weapon_effect(enemy)
            enemy.take_damage(damage)
            add_status_effect(enemy, "stagger", 1)
            print(_(f"Feint deals {damage} damage and staggers the enemy!"))
            if not enemy.is_alive():
                self.process_enemy_defeat(enemy)
        else:
            print(_("Feint misses."))

    def _skill_bandage(self, _enemy):
        if "bleed" in self.status_effects:
            del self.status_effects["bleed"]
            print(_("Bleeding stopped."))
        healed = self.heal(3)
        if healed > 0:
            print(_(f"You bandage your wounds and heal {healed} HP."))
        else:
            print(_("You are already at full health."))

    def _skill_guild_skill(self, enemy):
        damage = self.attack_power + 5
        self.apply_weapon_effect(enemy)
        enemy.take_damage(damage)
        print(_(f"Your guild training strikes for {damage} damage!"))

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
        healed = self.heal(20)
        print(_(f"You invoke Healing Light and recover {healed} health!"))

    def _skill_paladin(self, enemy):
        damage = self.attack_power + random.randint(5, 12)
        print(_(f"You smite the {enemy.name} for {damage} holy damage!"))
        enemy.take_damage(damage)
        healed = self.heal(10)
        if healed:
            print(_(f"Divine power heals you for {healed} HP!"))

    def _skill_bard(self, enemy):
        print(_("You play an inspiring tune, bolstering your spirit!"))
        add_status_effect(self, "inspire", 3)

    def _skill_barbarian(self, enemy):
        damage = self.attack_power + random.randint(8, 12)
        enemy.take_damage(damage)
        healed = self.heal(10)
        print(_(f"You enter a rage, dealing {damage} damage and healing {healed}!"))

    def _skill_druid(self, enemy):
        damage = self.attack_power + random.randint(5, 10)
        enemy.take_damage(damage)
        add_status_effect(enemy, "freeze", 1)
        healed = self.heal(5)
        print(_(f"Nature's wrath deals {damage} damage and restores {healed} health!"))

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
        healed = self.heal(damage // 2)
        print(_(f"Eldritch energy deals {damage} damage and heals you for {healed}!"))

    def _skill_necromancer(self, enemy):
        damage = self.attack_power + random.randint(5, 10)
        enemy.take_damage(damage)
        healed = self.heal(damage // 2)
        print(_(f"You siphon the enemy's soul for {damage} damage and {healed} health!"))

    def _skill_shaman(self, enemy):
        healed = self.heal(15)
        damage = self.attack_power + random.randint(4, 8)
        enemy.take_damage(damage)
        print(_(f"Spirits mend you for {healed} and shock the foe for {damage} damage!"))

    def _skill_alchemist(self, enemy):
        damage = self.attack_power + random.randint(8, 12)
        enemy.take_damage(damage)
        add_status_effect(enemy, "burn", 3)
        print(_(f"An explosive flask bursts for {damage} damage and sets the foe ablaze!"))

    def regen_stamina(self, amount):
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def wait(self):
        self.regen_stamina(10)
        print(_("You wait and catch your breath."))

    def use_skill(self, enemy, choice=None):
        if choice is None:
            print(_(f"[1] Power [2] Feint [3] Bandage STA: {self.stamina}/{self.max_stamina}"))
            choice = input(_("Choose skill: "))
        skill = self.skills.get(str(choice))
        if not skill:
            print(_("Invalid skill choice."))
            return None
        if skill["cooldown"] > 0:
            print(_(f"{skill['name']} is on cooldown for {skill['cooldown']} more turn(s)."))
            return None
        if self.stamina < skill["cost"]:
            needed = skill["cost"] - self.stamina
            print(_(f"You're winded (need {needed} more STA)."))
            return None
        self.stamina -= skill["cost"]
        skill["func"](enemy)
        skill["cooldown"] = skill["base_cooldown"]
        return skill["name"]

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
            print(_("You've unlocked Credit Finder: +5 credits after each kill."))
        if self.level == 5:
            print(_("You've unlocked Passive Regen: Heal 1 HP per move."))

    def join_guild(self, guild):
        if self.guild:
            print(_("You are already in a guild."))
            return
        self.guild = guild
        perks = GUILD_DEFS.get(guild, {})
        if "max_health" in perks:
            self.max_health += perks["max_health"]
            self.health += perks["max_health"]
        if "attack_power" in perks:
            self.attack_power += perks["attack_power"]
        if "cooldown_reduction" in perks:
            reduction = perks["cooldown_reduction"]
            for skill in self.skills.values():
                skill["base_cooldown"] = max(1, skill["base_cooldown"] - reduction)
                skill["cooldown"] = max(0, skill["cooldown"] - reduction)
        if "skill_cost_reduction" in perks:
            reduction = perks["skill_cost_reduction"]
            for skill in self.skills.values():
                skill["cost"] = max(0, skill["cost"] - reduction)
        skill_def = perks.get("skill")
        if skill_def:
            key = skill_def.get("key", "3")
            func = getattr(self, f"_skill_{skill_def['func']}", None)
            if func:
                self.skills[key] = {
                    "name": skill_def["name"],
                    "cost": skill_def["cost"],
                    "base_cooldown": skill_def["base_cooldown"],
                    "cooldown": 0,
                    "func": func,
                }
        self.guild_perks = perks.get("perks", [])
        print(_(f"You have joined the {guild}!"))

    def choose_race(self, race):
        self.race = race
        traits = RACE_DEFS.get(race, {})
        if "max_health" in traits:
            self.max_health += traits["max_health"]
            self.health += traits["max_health"]
        if "attack_power" in traits:
            self.attack_power += traits["attack_power"]
        self.racial_traits = traits.get("traits", [])
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

    def equip_armor(self, armor):
        if armor in self.inventory and isinstance(armor, Armor):
            if self.armor:
                self.inventory.append(self.armor)
                print(_(f"You unequipped the {self.armor.name}"))
            self.armor = armor
            self.inventory.remove(armor)
            print(_(f"You equipped the {armor.name}"))
        else:
            print(_("You don't have valid armor to equip."))

    def equip_trinket(self, trinket):
        if trinket in self.inventory and isinstance(trinket, Trinket):
            if self.trinket:
                self.inventory.append(self.trinket)
                print(_(f"You removed the {self.trinket.name}"))
            self.trinket = trinket
            self.inventory.remove(trinket)
            print(_(f"You equipped the {trinket.name}"))
        else:
            print(_("You don't have a valid trinket to equip."))

    def get_score_breakdown(self):
        """Return a detailed score breakdown.

        The base score is computed from the player's level, inventory size and
        credits. Style bonuses reward particular achievements such as completing a
        run without taking damage or leaving the dungeon wealthy. The result is
        returned as a dictionary detailing each component and the grand total.
        """

        breakdown = {
            "level": self.level * 100,
            "inventory": len(self.inventory) * 10,
            "credits": self.credits,
            "style": {},
        }

        if self.health == self.max_health:
            breakdown["style"]["no_damage"] = 50
        if self.credits >= 100:
            breakdown["style"]["rich"] = 50

        total = breakdown["level"] + breakdown["inventory"] + breakdown["credits"]
        total += sum(breakdown["style"].values())
        breakdown["total"] = total
        return breakdown

    def get_score(self):
        """Compatibility wrapper returning only the total score."""
        return self.get_score_breakdown()["total"]


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
        credits,
        ability=None,
        ai=None,
        speed=10,
        traits=None,
    ):
        super().__init__(name, "")
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.defense = defense
        self.credits = credits
        self.ability = ability
        self.ai = ai
        self.xp = 10
        self.speed = speed
        self.traits = traits or []
        # Intent planning and cooldowns
        self.next_action = None
        self.intent = None
        self.intent_message = ""
        self.heavy_cd = 0

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        if "shield" in self.status_effects:
            damage = max(0, damage - 5)
            print(_(f"The {self.name}'s shield absorbs 5 damage!"))
        if "armored" in self.traits:
            damage = max(0, damage - 3)
            print(_(f"The {self.name}'s armor softens the blow!"))
        self.health = max(0, self.health - damage)

    def drop_credits(self):
        return self.credits

    def apply_status_effects(self):
        """Delegate to the shared status effect helper and traits."""
        skip = apply_effects(self)
        if "regenerator" in self.traits and self.health > 0:
            heal = min(5, self.max_health - self.health)
            if heal > 0:
                self.health += heal
                print(_(f"The {self.name} regenerates {heal} health!"))
        return skip

    def defend(self):
        add_status_effect(self, "shield", 1)
        print(_(f"The {self.name} raises its guard!"))

    def take_turn(self, player):
        action = self.next_action
        self.next_action = None
        self.intent = None
        if action is None:
            if self.ai:
                action = self.ai.choose_action(self, player)
            else:
                action = "attack"
        if action == "defend":
            self.defend()
        elif action == "heavy_attack":
            add_status_effect(self, "heavy", 1)
            self.heavy_cd = 3
            self.attack(player)
        elif action == "wild_attack":
            add_status_effect(self, "wild", 1)
            self.attack(player)
        else:
            self.attack(player)

    def attack(self, player):
        hit_chance = 60
        if self.status_effects.pop("advantage", 0):
            hit_chance += 15
        if self.status_effects.pop("stagger", 0):
            hit_chance -= 20
        if self.status_effects.pop("wild", 0):
            hit_chance -= 20
            wild = True
        else:
            wild = False
        if "blessed" in self.status_effects:
            hit_chance += 10
        if "cursed" in self.status_effects:
            hit_chance -= 5
        roll = random.randint(1, 100)
        damage = random.randint(self.attack_power // 2, self.attack_power)
        damage = int(damage * RARITY_MODIFIERS.get(self.rarity, 1.0))
        if self.status_effects.pop("heavy", 0):
            damage = int(damage * 1.5)
        if "berserker" in self.traits and self.health <= self.max_health // 2:
            damage = int(damage * 1.5)
            print(_(f"The {self.name} goes berserk!"))
        if roll <= hit_chance:
            if wild and roll >= 95:
                damage *= 2
                print(_(f"The {self.name} lands a vicious critical!"))
            if self.ability == "lifesteal":
                self.health += damage // 3
                print(_(f"The {self.name} drains life and heals for {damage // 3}!"))
            elif self.ability == "poison":
                dur = int(3 * RARITY_MODIFIERS.get(self.rarity, 1.0))
                add_status_effect(player, "poison", dur)
            elif self.ability == "burn":
                dur = int(3 * RARITY_MODIFIERS.get(self.rarity, 1.0))
                add_status_effect(player, "burn", dur)
            elif self.ability == "stun":
                dur = int(1 * RARITY_MODIFIERS.get(self.rarity, 1.0))
                add_status_effect(player, "stun", dur)
            elif self.ability == "bleed":
                dur = int(3 * RARITY_MODIFIERS.get(self.rarity, 1.0))
                add_status_effect(player, "bleed", dur)
            elif self.ability == "freeze":
                dur = int(1 * RARITY_MODIFIERS.get(self.rarity, 1.0))
                add_status_effect(player, "freeze", dur)
            elif self.ability == "double_strike" and random.random() < 0.25:
                print(_(f"The {self.name} strikes twice!"))
                player.take_damage(damage, source=self.name)
            player.take_damage(damage, source=self.name)
            if config.verbose_combat:
                print(
                    _(
                        f"{self.name} attacks ({hit_chance}%): roll {roll} → HIT. Damage {damage}.",
                    )
                )
            else:
                print(_(f"The {self.name} attacked you and dealt {damage} damage."))
        else:
            if config.verbose_combat:
                reason = "It slipped on the wet stone!"
                print(
                    _(
                        f"{self.name} attacks ({hit_chance}%): roll {roll} → MISS. {reason}",
                    )
                )
            else:
                print(_(f"The {self.name}'s attack missed."))


def create_guild_champion(player: Player) -> Enemy:
    """Create a boss that mirrors the player's basic stats."""

    return Enemy(
        "Guild Champion",
        player.max_health,
        player.attack_power,
        0,
        0,
    )


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
            healed = player.heal(self.heal_amount)
            if healed > 0:
                print(_(f"{self.name} heals {player.name} for {healed} HP!"))
