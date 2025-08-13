"""Simple terminal based renderer for the dungeon crawler.

The renderer is intentionally lightweight – it only knows how to display text
messages and is completely agnostic of game logic.  It can subscribe to the
core event stream by being passed an ``event_bus`` object that exposes a
``subscribe`` method.  When events are received their ``message`` attribute is
printed using the provided ``output_func``.
"""

from __future__ import annotations

from gettext import gettext as _
from typing import Callable

from ..core.events import Event


class Renderer:
    """Minimal text based renderer used by the test-suite.

    Parameters
    ----------
    event_bus:
        Optional object supporting a ``subscribe`` method.  If provided the
        renderer will register its :meth:`handle_event` callback to automatically
        display events as they are published.
    output_func:
        Callable used to output text. Defaults to :func:`print` making the
        renderer suitable for CLI based interfaces and for capturing output in
        tests.
    """

    def __init__(self, event_bus: object | None = None, output_func: Callable[[str], None] = print):
        self.output_func = output_func
        self.lines: list[str] = []
        if event_bus is not None and hasattr(event_bus, "subscribe"):
            event_bus.subscribe(self.handle_event)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def handle_event(self, event: Event) -> None:
        """Display a core event."""

        self.show_message(_(event.message))

    # ------------------------------------------------------------------
    # Basic message helpers
    # ------------------------------------------------------------------
    def show_message(self, text: str) -> None:
        """Display ``text`` to the user and store it in ``lines``."""

        self.lines.append(text)
        self.output_func(text)

    def show_status(self, game_state) -> None:
        """Render a summary of the current ``game_state``."""

        player = game_state.player
        status = _(
            f"Health: {player.health}/{player.max_health} | STA: {player.stamina}/{player.max_stamina} | "
            f"XP: {player.xp} | Gold: {player.gold} | Level: {player.level} | Floor: {game_state.current_floor}"
        )
        self.show_message(status)

    def draw_map(self, map_string: str) -> None:
        """Render ``map_string`` representing the dungeon layout."""

        for line in map_string.split("\n"):
            self.show_message(line)


__all__ = ["Renderer"]
