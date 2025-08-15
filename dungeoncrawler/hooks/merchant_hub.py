"""Hook providing merchant hub behaviour."""

from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Placeholder for merchant hub rule."""

    def __init__(self) -> None:
        self.enabled = False

    def on_floor_start(self, state, floor_def) -> None:  # noqa: D401
        """Read merchant hub configuration and trigger the shop."""
        self.enabled = bool(floor_def.rule_mods.get("merchant_hub"))
        if self.enabled:
            state.game.restock_shop()
            state.game.shop()
