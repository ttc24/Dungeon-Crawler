"""Hook managing mirror shadow encounters."""

from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Skeleton implementation for mirror shadows."""

    def __init__(self) -> None:
        self.enabled = False

    def on_floor_start(self, state, floor_def) -> None:  # noqa: D401
        """Capture mirror shadow settings."""
        self.enabled = bool(floor_def.rule_mods.get("mirror_shadows"))
