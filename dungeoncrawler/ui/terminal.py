"""Simple terminal based renderer for the dungeon crawler.

The renderer is intentionally lightweight – it only knows how to display text
messages and is completely agnostic of game logic.  It can subscribe to the
core event stream by being passed an ``event_bus`` object that exposes a
``subscribe`` method.  When events are received their ``message`` attribute is
printed using the provided ``output_func``.
"""

from __future__ import annotations

import time
from gettext import gettext as _
from typing import Callable

from rich.console import Console
from rich.table import Table
from rich.text import Text

from ..config import config
from ..core.events import Event

# Basic palettes for map rendering
DEFAULT_PALETTE = {"@": "green", "E": "red", ".": "white", "·": "grey70", "#": "grey50"}
COLORBLIND_PALETTE = {"@": "cyan", "E": "magenta", ".": "white", "·": "grey70", "#": "grey50"}


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
        self.console = Console()
        self.lines: list[str] = []
        self.palette = COLORBLIND_PALETTE if config.colorblind_mode else DEFAULT_PALETTE
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
    def show_message(self, text: str, style: str | None = None) -> None:
        """Display ``text`` to the user and store it in ``lines``."""

        self.lines.append(text)
        self.console.print(text, style=style)
        if config.slow_messages:
            time.sleep(config.key_repeat_delay)
        if self.output_func is not print:
            self.output_func(text)

    def show_status(self, game_state) -> None:
        """Render a summary of the current ``game_state``."""

        player = game_state.player
        table = Table(box=None, show_header=False)
        table.add_row("Health", f"[green]{player.health}/{player.max_health}")
        table.add_row("STA", f"{player.stamina}/{player.max_stamina}")
        table.add_row("XP", str(player.xp))
        table.add_row("Gold", str(player.gold))
        table.add_row("Level", str(player.level))
        table.add_row("Floor", str(game_state.current_floor))
        self.console.print(table)
        status = _(
            f"Health: {player.health}/{player.max_health} | STA: {player.stamina}/{player.max_stamina} | "
            f"XP: {player.xp} | Gold: {player.gold} | Level: {player.level} | Floor: {game_state.current_floor}"
        )
        if self.output_func is not print:
            self.output_func(status)
        self.lines.append(status)

    def draw_map(self, map_string: str) -> None:
        """Render ``map_string`` representing the dungeon layout."""

        for line in map_string.split("\n"):
            text = Text()
            for char in line:
                text.append(char, style=self.palette.get(char, ""))
            self.console.print(text)
            if self.output_func is not print:
                self.output_func(line)
            self.lines.append(line)


# Public API
__all__ = ["Renderer"]
