from dataclasses import dataclass, field
from typing import Optional

# Rarity modifiers used to scale damage and effect durations
RARITY_MODIFIERS = {
    "common": 1.0,
    "rare": 1.2,
    "epic": 1.5,
}


@dataclass
class Item:
    """Simple item with a name and description."""

    name: str
    description: str


@dataclass
class Weapon(Item):
    """Weapon that can deal a range of damage and may apply an effect."""

    min_damage: int
    max_damage: int
    price: int = 50
    rarity: str = "common"
    effect: Optional[str] = field(default=None)


@dataclass
class Armor(Item):
    """Defensive equipment that mitigates incoming damage."""

    defense: int
    price: int = 40
    rarity: str = "common"
    effect: Optional[str] = field(default=None)


@dataclass
class Trinket(Item):
    """Accessory that can apply special effects."""

    effect: Optional[str] = None
    price: int = 30
    rarity: str = "common"


@dataclass
class Augment(Item):
    """Item that grants a bonus at a permanent cost.

    Augments offer a risk-reward choice by increasing attack power while
    reducing maximum health. Multiple copies of the same augment may stack up
    to ``max_stacks`` times to amplify both the benefit and the drawback.
    """

    attack_bonus: int
    health_penalty: int
    max_stacks: int = 1
    price: int = 0
    rarity: str = "common"
    combos_with: Optional[list[str]] = None

    def describe(self) -> str:
        base = self.description
        if self.combos_with:
            combo = ", ".join(self.combos_with)
            base = f"{base} Combos with: {combo}"
        return base
