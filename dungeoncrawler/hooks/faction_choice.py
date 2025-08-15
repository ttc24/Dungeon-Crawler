"""Hook storing player faction selections."""

from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Provide faction choice interactions."""

    def __init__(self) -> None:
        self.options: list[str] = []

    def on_floor_start(self, state, floor_def) -> None:  # noqa: D401
        """Load available faction choices from rules."""
        cfg = floor_def.rule_mods.get("faction_choice", {})
        self.options = list(cfg.get("options", []))
