"""Simple terminal renderer for core events.

This renderer has no game logic.  It merely subscribes to events produced by
core modules and forwards their text to the provided ``output_func`` which
defaults to :func:`print`.
"""

from __future__ import annotations

from typing import Iterable

from ..core.events import Event
from gettext import gettext as _


class Renderer:
    """Minimal text based renderer used by the test-suite."""

    def __init__(self, output_func=print):
        self.output_func = output_func

    # ------------------------------------------------------------------
    # Basic message helpers
    # ------------------------------------------------------------------
    def show_message(self, text: str) -> None:
        """Display ``text`` to the user."""

        self.output_func(text)

    def show_status(self, game_state) -> None:
        """Render a summary of the current ``game_state``."""

        player = game_state.player
        status = _(
            f"Health: {player.health}/{player.max_health} | STA: {player.stamina}/{player.max_stamina} | "
            f"XP: {player.xp} | Gold: {player.gold} | Level: {player.level} | Floor: {game_state.current_floor}"
        )
        self.output_func(status)

    def draw_map(self, map_string: str) -> None:
        """Render ``map_string`` representing the dungeon layout."""

        self.output_func(map_string)

    # ------------------------------------------------------------------
    # Event rendering
    # ------------------------------------------------------------------
    def render_events(self, events: Iterable[Event]) -> None:
        """Render a sequence of :class:`~dungeoncrawler.core.events.Event`.

        Each event's ``message`` attribute is forwarded to ``output_func``.  The
        renderer itself contains no game logic; callers are responsible for
        producing the events.
        """

        for event in events:
            self.output_func(event.message)
