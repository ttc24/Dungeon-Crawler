"""Hook skeleton for moving wall mechanics."""

from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Placeholder implementation for moving walls."""

    def __init__(self) -> None:
        self.enabled = False

    def on_floor_start(self, state, floor_def) -> None:  # noqa: D401
        """Initialise moving wall settings."""
        cfg = floor_def.rule_mods.get("moving_walls")
        self.enabled = bool(cfg)
