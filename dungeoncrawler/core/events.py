"""Typed event objects produced by core game mechanics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Event:
    """Base class for all core events."""

    message: str


@dataclass
class AttackResolved(Event):
    """Result of a combat attack action."""

    attacker: str
    defender: str
    damage: int
    defeated: bool


@dataclass
class StatusApplied(Event):
    """A temporary status was applied to an entity."""

    target: str
    status: str
    duration: int
    value: int = 0


@dataclass
class TileDiscovered(Event):
    """A new map tile has been revealed to the player."""

    x: int
    y: int


@dataclass
class ItemGained(Event):
    """An item was added to an entity's inventory."""

    owner: str
    item: str
    amount: int = 1
