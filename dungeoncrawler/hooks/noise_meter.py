"""Hook tracking player noise generation."""

from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Basic noise meter implementation."""

    def __init__(self) -> None:
        self.threshold = 0

    def on_floor_start(self, state, floor_def) -> None:  # noqa: D401
        """Read noise meter configuration."""
        cfg = floor_def.rule_mods.get("noise_meter", {})
        self.threshold = cfg.get("threshold", 0)

