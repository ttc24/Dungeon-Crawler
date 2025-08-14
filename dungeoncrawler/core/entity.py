"""Lightweight entity model used by the deterministic combat resolver."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterator, List, Optional, Tuple, TypedDict, cast

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
    weapon: Optional[str] = None
    armor: Optional[str] = None
    trinket: Optional[str] = None
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


class ArchetypeData(TypedDict):
    stats: Dict[str, int]
    intent: Callable[[], Iterator[Tuple[str, str]]]
    rarity: str


def _load_archetypes() -> Dict[str, ArchetypeData]:
    data = load_enemies()
    archetypes: Dict[str, ArchetypeData] = {}
    for name, cfg in data.items():
        stats_cfg: Dict[str, int] = cast(Dict[str, int], cfg.get("stats", {}))
        intents_cfg: List[Dict[str, str]] = cast(List[Dict[str, str]], cfg.get("intents", []))
        rarity_cfg: str = cast(str, cfg.get("rarity", "common"))
        archetypes[name] = {
            "stats": stats_cfg,
            "intent": _make_intent_factory(intents_cfg),
            "rarity": rarity_cfg,
        }
    return archetypes


ARCHETYPES: Dict[str, ArchetypeData] = _load_archetypes()


def make_enemy(archetype: str) -> Entity:
    """Create an :class:`Entity` for the given enemy archetype."""

    data = ARCHETYPES[archetype]
    stats = dict(data["stats"])
    intent_gen = data["intent"]()
    return Entity(archetype, stats, intent=intent_gen, rarity=data["rarity"])
