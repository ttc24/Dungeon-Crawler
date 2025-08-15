"""Floor hook implementing water movement penalties and breath limits."""

from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Apply water slow and breath timer rules."""

    def __init__(self) -> None:
        self.config: dict = {}

    def on_floor_start(self, state, floor_def) -> None:  # noqa: D401
        """Store water configuration for later use."""
        self.config = floor_def.rule_mods.get("water", {})

