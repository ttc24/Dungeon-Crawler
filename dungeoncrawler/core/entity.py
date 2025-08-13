"""Lightweight entity model used by the deterministic combat resolver."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Tuple


@dataclass
class Entity:
    """Simple entity with stats, inventory and status tracking.

    Parameters
    ----------
    name:
        Display name of the entity.
    stats:
        Mapping of stat names to integer values. Common keys are
        ``health``, ``attack`` and ``defense`` but the resolver does not
        impose a strict schema.
    inventory:
        Collection of item identifiers owned by the entity.
    status:
        List of textual status flags such as ``"defending"``.
    """

    name: str
    stats: Dict[str, int]
    inventory: List[str] = field(default_factory=list)
    status: List[str] = field(default_factory=list)
    intent: Optional[Iterator[Tuple[str, str]]] = None

    # ------------------------------------------------------------------
    def is_alive(self) -> bool:
        """Return ``True`` if the entity's ``health`` stat is above zero."""

        return self.stats.get("health", 0) > 0


# ---------------------------------------------------------------------------
# Enemy archetypes
# ---------------------------------------------------------------------------


def _goblin_skirm_intents() -> Iterator[Tuple[str, str]]:
    while True:
        yield "attack", "Goblin darts forward with a rusty blade."


def _guard_beetle_intents() -> Iterator[Tuple[str, str]]:
    while True:
        yield "defend", "Beetle curls into its shell."
        yield "attack", "Beetle snaps out with its mandibles."


def _rabid_bat_intents() -> Iterator[Tuple[str, str]]:
    while True:
        yield "attack", "Bat screeches and dives."


def _cult_acolyte_intents() -> Iterator[Tuple[str, str]]:
    while True:
        yield "attack", "Acolyte begins channeling dark energy."


ARCHETYPES: Dict[str, Dict[str, object]] = {
    "Goblin Skirm": {
        "stats": {"health": 6, "attack": 3, "defense": 1, "speed": 4},
        "intent": _goblin_skirm_intents,
    },
    "Guard Beetle": {
        "stats": {"health": 12, "attack": 2, "defense": 4, "speed": 2},
        "intent": _guard_beetle_intents,
    },
    "Rabid Bat": {
        "stats": {"health": 5, "attack": 2, "defense": 0, "speed": 6},
        "intent": _rabid_bat_intents,
    },
    "Cult Acolyte": {
        "stats": {"health": 8, "attack": 4, "defense": 1, "speed": 3},
        "intent": _cult_acolyte_intents,
    },
}


def make_enemy(archetype: str) -> Entity:
    """Create an :class:`Entity` for the given enemy archetype."""

    data = ARCHETYPES[archetype]
    # copy stats to avoid shared state between entities
    stats = dict(data["stats"])
    intent_gen = data["intent"]()
    return Entity(archetype, stats, intent=intent_gen)
