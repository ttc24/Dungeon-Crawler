"""Graphical user interface built with the optional :mod:`textual` library.

This module is imported only when the third‑party dependency is available.  It
provides :class:`DungeonApp`, a small showcase application composed of several
resizable panels.  Importing this file without :mod:`textual` installed will
raise :class:`ModuleNotFoundError` with a helpful message.
"""

from __future__ import annotations

try:  # pragma: no cover - import guard exercised in __init__
    from textual.app import App, ComposeResult
    from textual.containers import Grid
    from textual.widgets import Static
except ModuleNotFoundError as exc:  # pragma: no cover - textual not installed
    raise ModuleNotFoundError("`textual` is required to use DungeonApp") from exc


class MapPanel(Static):
    """Panel displaying the dungeon map."""


class StatsPanel(Static):
    """Panel showing player statistics."""


class LogPanel(Static):
    """Panel containing recent messages."""


class ActionsPanel(Static):
    """Panel listing available actions."""


class DungeonApp(App):
    """Textual interface composed of resizable panels."""

    CSS = (
        ".grid {grid-size: 2 2; grid-columns: 2fr 1fr; grid-rows: 3fr 1fr;}\n"
        "#map {grid-column: 1; grid-row: 1 / span 2;}\n"
        "#stats {grid-column: 2; grid-row: 1;}\n"
        "#log {grid-column: 2; grid-row: 2;}\n"
        "#actions {grid-column: 1; grid-row: 2;}\n"
    )

    def compose(self) -> ComposeResult:
        with Grid(classes="grid"):
            yield MapPanel("Map", id="map")
            yield StatsPanel("Stats", id="stats")
            yield LogPanel("Log", id="log")
            yield ActionsPanel("Actions", id="actions")


__all__ = ["DungeonApp"]
