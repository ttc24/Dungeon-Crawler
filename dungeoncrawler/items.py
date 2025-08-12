from dataclasses import dataclass, field
from typing import Optional


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
    effect: Optional[str] = field(default=None)
