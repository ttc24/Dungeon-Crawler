"""Lightweight entity model used by the deterministic combat resolver."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Tuple

from .data import load_enemies


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
    rarity: str = "common"

    # ------------------------------------------------------------------
    def is_alive(self) -> bool:
        """Return ``True`` if the entity's ``health`` stat is above zero."""

        return self.stats.get("health", 0) > 0


# ---------------------------------------------------------------------------
# Enemy archetypes
# ---------------------------------------------------------------------------

def _make_intent_factory(intents: List[Dict[str, str]]):
    def generator() -> Iterator[Tuple[str, str]]:
        while True:
            for entry in intents:
                yield entry.get("action", "attack"), entry.get("message", "")

    return generator


def _load_archetypes() -> Dict[str, Dict[str, object]]:
    data = load_enemies()
    archetypes: Dict[str, Dict[str, object]] = {}
    for name, cfg in data.items():
        archetypes[name] = {
            "stats": cfg.get("stats", {}),
            "intent": _make_intent_factory(cfg.get("intents", [])),
            "rarity": cfg.get("rarity", "common"),
        }
    return archetypes


ARCHETYPES = _load_archetypes()


def make_enemy(archetype: str) -> Entity:
    """Create an :class:`Entity` for the given enemy archetype."""

    data = ARCHETYPES[archetype]
    stats = dict(data["stats"])
    intent_gen = data["intent"]()
    return Entity(archetype, stats, intent=intent_gen, rarity=data.get("rarity", "common"))
