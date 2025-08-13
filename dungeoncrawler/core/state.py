"""Game state container for dungeon crawler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from .map import GameMap

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from ..entities import Player


@dataclass
class GameState:
    """Lightweight container storing the current game state.

    Attributes
    ----------
    seed:
        RNG seed used for deterministic behaviour.
    current_floor:
        The active dungeon floor number.
    player:
        The player entity exploring the dungeon.
    game_map:
        Map data including grid layout and visibility arrays.
    log:
        In-memory buffer of game messages.
    """

    seed: int
    current_floor: int
    player: Optional["Player"]
    game_map: GameMap
    log: List[str] = field(default_factory=list)

    def queue_message(self, message: str) -> None:
        """Append ``message`` to the log buffer."""
        self.log.append(message)
