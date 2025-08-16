from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks
from dungeoncrawler.status_effects import add_status_effect


class Hooks(FloorHooks):
    """Mana Lock and Hex of Dull Wards mechanics for Floor 13."""

    def on_floor_start(self, state, floor):
        player = state.player
        if player:
            # Apply long-lasting debuffs for this floor
            add_status_effect(player, "mana_lock", 1)
            add_status_effect(player, "dull_wards", 1)
