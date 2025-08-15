"""Legacy rendering helpers.

This module previously housed the :class:`Renderer` implementation used by the
tests.  The class has now moved to :mod:`dungeoncrawler.ui.terminal` but is
re-exported here for backwards compatibility.  The map rendering utilities
remain in this module.
"""

from __future__ import annotations

from .ui.terminal import Renderer  # re-export for existing imports

# ----------------------------------------------------------------------
# Map rendering utilities – migrated from :mod:`map`
# ----------------------------------------------------------------------


def render_map_string(game) -> str:
    """Return a simple string representation of the dungeon map."""

    rows = []
    for y in range(game.height):
        row = ""
        for x in range(game.width):
            if game.visible[y][x]:
                if (x, y) == (game.player.x, game.player.y):
                    row += "@"
                elif (x, y) == game.exit_coords:
                    row += "E"
                else:
                    row += "."
            elif game.discovered[y][x]:
                row += "·"
            else:
                row += " "
        rows.append(row)
    return "\n".join(rows)


def render_map(game) -> None:
    """Simple helper that prints the current map using :func:`render_map_string`."""

    renderer = getattr(game, "renderer", Renderer())
    renderer.draw_map(render_map_string(game))


# Public API
__all__ = ["Renderer", "render_map", "render_map_string"]
