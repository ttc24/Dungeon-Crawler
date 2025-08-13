"""Map rendering helpers.

The original project exposed a small ``Renderer`` class from this module.  The
renderer now lives in :mod:`dungeoncrawler.ui.terminal`; this file only retains
helpers for producing map strings and a convenience wrapper around the active
renderer.
"""

from __future__ import annotations

from .ui.terminal import Renderer


def render_map_string(game) -> str:
    """Return a simple string representation of the dungeon map."""

    rows: list[str] = []
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
                row += "#"
        rows.append(row)
    return "\n".join(rows)


def render_map(game) -> None:
    """Print the current map using :func:`render_map_string`."""

    renderer = getattr(game, "renderer", Renderer())
    renderer.draw_map(render_map_string(game))

