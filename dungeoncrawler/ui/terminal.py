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

# ``rich`` is an optional dependency.  When it is not available we fall back to
# very small stand‑ins that implement just the pieces of API used in the test
# suite.  This keeps the package lightweight while avoiding import errors in
# environments where ``rich`` is absent.

try:  # pragma: no cover - exercised indirectly in the tests
    from rich.console import Console  # type: ignore
    from rich.table import Table  # type: ignore
    from rich.text import Text  # type: ignore
except ModuleNotFoundError:  # pragma: no cover

    class Console:
        """Very small subset of :class:`rich.console.Console`.

        Only the :meth:`print` method is required which simply proxies to the
        builtin :func:`print`.
        """

        def print(self, *args, **kwargs):  # noqa: D401 - small helper
            print(*args)

    class Table:
        """Minimal table that stores rows and prints them plainly."""

        def __init__(self, *args, **kwargs):
            self.rows: list[tuple[str, str]] = []

        def add_row(self, *columns: str) -> None:
            self.rows.append(tuple(columns))

        def __str__(self) -> str:  # pragma: no cover - trivial
            return "\n".join("\t".join(row) for row in self.rows)

    class Text:
        """Simple stand in for :class:`rich.text.Text`.

        The real ``Text`` type allows rich styling.  For the purposes of the
        tests we only need to accumulate plain characters, so this class keeps a
        list of fragments which are joined when converted to ``str``.
        """

        def __init__(self) -> None:
            self.fragments: list[str] = []

        def append(self, text: str, style: str | None = None) -> None:
            self.fragments.append(text)

        def __str__(self) -> str:  # pragma: no cover - trivial
            return "".join(self.fragments)


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
        self.legend_visible = False
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

        if self.legend_visible:
            legend = [
                _("Legend:"),
                _(" @ - You"),
                _(" E - Exit"),
                _(" . - Floor"),
                _(" · - Discovered"),
                _(" # - Unexplored"),
            ]
            for entry in legend:
                self.show_message(entry)

    def toggle_legend(self) -> None:
        """Toggle display of the map legend."""

        self.legend_visible = not self.legend_visible


# Public API
__all__ = ["Renderer"]
