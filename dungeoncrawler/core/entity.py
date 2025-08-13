"""Lightweight entity model used by the deterministic combat resolver."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


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

    # ------------------------------------------------------------------
    def is_alive(self) -> bool:
        """Return ``True`` if the entity's ``health`` stat is above zero."""

        return self.stats.get("health", 0) > 0
