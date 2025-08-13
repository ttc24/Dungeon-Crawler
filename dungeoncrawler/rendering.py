"""Rendering helpers and UI abstractions.

This module centralises all user interface interactions.  Game logic
modules interact with :class:`Renderer` instead of printing directly so the
core game remains easy to test.
"""

from __future__ import annotations

from gettext import gettext as _


class Renderer:
    """Minimal text based renderer used by the test-suite.

    Real front ends may subclass this and provide richer implementations but
    the methods here are purposely tiny – they simply forward output to the
    supplied ``output_func`` which defaults to :func:`print`.
    """

    def __init__(self, output_func=print):
        self.output_func = output_func

    # ------------------------------------------------------------------
    # Basic message helpers
    # ------------------------------------------------------------------
    def show_message(self, text: str) -> None:
        """Display ``text`` to the user."""

        self.output_func(text)

    def show_status(self, game_state) -> None:
        """Render a summary of the current ``game_state``.

        Only a few core stats are shown which keeps the method independent of
        any particular front end.  Additional data can be appended by callers
        if desired.
        """

        player = game_state.player
        status = _(f"Health: {player.health}/{player.max_health} | STA: {player.stamina}/{player.max_stamina} | "
                   f"XP: {player.xp} | Gold: {player.gold} | Level: {player.level} | Floor: {game_state.current_floor}")
        self.output_func(status)

    def draw_map(self, map_string: str) -> None:
        """Render ``map_string`` representing the dungeon layout."""

        self.output_func(map_string)


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

