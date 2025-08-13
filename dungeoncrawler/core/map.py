"""Map representation and visibility helpers."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, List, Optional, Set, Tuple

from .events import TileDiscovered

Tile = Optional[Any]


@dataclass
class GameMap:
    """Grid based dungeon map with fog-of-war support."""

    grid: List[List[Tile]]
    discovered: List[List[bool]] = field(init=False)
    visible: List[List[bool]] = field(init=False)

    def __post_init__(self) -> None:  # pragma: no cover - simple initialisation
        height = len(self.grid)
        width = len(self.grid[0]) if height else 0
        self.discovered = [[False for _ in range(width)] for _ in range(height)]
        self.visible = [[False for _ in range(width)] for _ in range(height)]

    # ------------------------------------------------------------------
    # Fog of war utilities
    # ------------------------------------------------------------------
    def compute_visibility(self, px: int, py: int, radius: int) -> Set[Tuple[int, int]]:
        """Return coordinates visible from ``(px, py)`` using BFS."""

        height = len(self.grid)
        width = len(self.grid[0]) if height else 0
        visited: Set[Tuple[int, int]] = set()
        queue = deque([(px, py, 0)])
        while queue:
            x, y, dist = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if dist >= radius:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and self.grid[ny][nx] is not None:
                    queue.append((nx, ny, dist + 1))
        return visited

    def update_visibility(self, px: int, py: int, radius: int) -> List[TileDiscovered]:
        """Recompute visibility arrays starting from ``(px, py)``.

        Returns a list of :class:`TileDiscovered` events for any tiles newly
        revealed during this update.
        """

        self.visible = [[False for _ in row] for row in self.grid]
        events: List[TileDiscovered] = []
        for x, y in self.compute_visibility(px, py, radius):
            self.visible[y][x] = True
            if not self.discovered[y][x]:
                self.discovered[y][x] = True
                events.append(TileDiscovered(f"Tile ({x},{y}) discovered", x, y))
        return events


def compute_visibility(
    grid: List[List[Tile]], px: int, py: int, radius: int
) -> Set[Tuple[int, int]]:
    """Convenience wrapper around :meth:`GameMap.compute_visibility`."""
    return GameMap(grid).compute_visibility(px, py, radius)


def update_visibility(game) -> List[TileDiscovered]:
    """Update ``game`` object's visibility arrays in-place.

    Returns a list of :class:`TileDiscovered` events for tiles newly seen by the
    player.
    """

    gm = GameMap(game.rooms)
    gm.discovered = game.discovered
    gm.visible = [[False for __ in range(game.width)] for __ in range(game.height)]
    radius = 6 if getattr(game, "current_floor", 1) == 1 else 3 + game.current_floor // 2
    events = gm.update_visibility(game.player.x, game.player.y, radius)
    game.visible = gm.visible
    game.discovered = gm.discovered
    return events
