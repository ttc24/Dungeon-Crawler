"""Utility for rendering the dungeon map.

This module provides a :class:`MapRenderer` that can draw the current
state of a :class:`~dungeoncrawler.dungeon.DungeonBase` instance using the
`curses` library.  The renderer colours different tile types and supports
displaying a small legend that explains the symbols.  The legend can be
toggle at runtime by pressing ``?`` when the map is displayed.

The renderer also exposes :meth:`MapRenderer.render_to_string` which
generates the coloured map as a plain string.  This is used by the unit
tests to perform snapshot style assertions without requiring a real
terminal environment.
"""

from __future__ import annotations

import curses
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple


# ---------------------------------------------------------------------------
# Colour and symbol configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TileAppearance:
    symbol: str
    colour_name: str


TILES: Dict[str, TileAppearance] = {
    "player": TileAppearance("@", "player"),
    "visited": TileAppearance(".", "visited"),
    "unseen": TileAppearance("#", "unseen"),
    "exit": TileAppearance("E", "exit"),
}


COLOUR_PAIRS = {
    "player": 1,
    "visited": 2,
    "unseen": 3,
    "exit": 4,
}

# ANSI colour codes used for ``render_to_string``.  These mirror the curses
# colours but allow tests to easily assert the output of the renderer.
ANSI_COLOURS = {
    "player": 36,  # cyan
    "visited": 37,  # white
    "unseen": 90,  # bright black / grey
    "exit": 35,  # magenta
}

LEGEND = {
    TILES["player"].symbol: "Player",
    TILES["visited"].symbol: "Visited",
    TILES["unseen"].symbol: "Unseen",
    TILES["exit"].symbol: "Exit",
}


class MapRenderer:
    """Render a dungeon map using curses or plain strings."""

    def __init__(self, dungeon: "DungeonBase"):
        self.dungeon = dungeon
        self.show_legend = False

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _tile_at(self, x: int, y: int) -> TileAppearance:
        pos = (x, y)
        if pos == (self.dungeon.player.x, self.dungeon.player.y):
            key = "player"
        elif pos == getattr(self.dungeon, "exit_coords", None):
            key = "exit"
        elif pos in getattr(self.dungeon, "visited_rooms", set()):
            key = "visited"
        else:
            key = "unseen"
        return TILES[key]

    def _colourise(self, symbol: str, colour_name: str) -> str:
        code = ANSI_COLOURS[colour_name]
        return f"\x1b[{code}m{symbol}\x1b[0m"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def render_to_string(self, show_legend: bool = False) -> str:
        """Return the map as a colourised string.

        Parameters
        ----------
        show_legend:
            If ``True`` a legend describing the map symbols will be appended
            to the returned string.
        """

        lines = []
        for y in range(self.dungeon.height):
            row_symbols = []
            for x in range(self.dungeon.width):
                tile = self._tile_at(x, y)
                row_symbols.append(self._colourise(tile.symbol, tile.colour_name))
            lines.append("".join(row_symbols))

        if show_legend:
            lines.append("")
            for sym, desc in LEGEND.items():
                colour = TILES[[k for k, v in TILES.items() if v.symbol == sym][0]].colour_name
                lines.append(f"{self._colourise(sym, colour)} - {desc}")

        return "\n".join(lines)

    # Curses based rendering ------------------------------------------------
    def _init_colours(self) -> None:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOUR_PAIRS["player"], curses.COLOR_CYAN, -1)
        curses.init_pair(COLOUR_PAIRS["visited"], curses.COLOR_WHITE, -1)
        curses.init_pair(COLOUR_PAIRS["unseen"], curses.COLOR_BLACK, -1)
        curses.init_pair(COLOUR_PAIRS["exit"], curses.COLOR_MAGENTA, -1)

    def _draw(self, stdscr) -> None:
        stdscr.clear()
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                tile = self._tile_at(x, y)
                colour = curses.color_pair(COLOUR_PAIRS[tile.colour_name])
                stdscr.addstr(y, x, tile.symbol, colour)

        if self.show_legend:
            offset = self.dungeon.height + 1
            for i, (sym, desc) in enumerate(LEGEND.items()):
                colour_name = TILES[[k for k, v in TILES.items() if v.symbol == sym][0]].colour_name
                colour = curses.color_pair(COLOUR_PAIRS[colour_name])
                stdscr.addstr(offset + i, 0, sym, colour)
                stdscr.addstr(offset + i, 2, f"- {desc}")

        stdscr.refresh()

    def _curses_loop(self, stdscr) -> None:
        self._init_colours()
        curses.curs_set(0)
        self._draw(stdscr)
        while True:
            key = stdscr.getch()
            if key == ord('?'):
                self.show_legend = not self.show_legend
                self._draw(stdscr)
            elif key in (ord('q'), 27):
                break

    def run(self) -> None:
        """Display the map using curses.

        The user can press ``?`` to toggle the legend or ``q``/``ESC`` to
        exit the map view.
        """

        curses.wrapper(self._curses_loop)


__all__ = ["MapRenderer"]

