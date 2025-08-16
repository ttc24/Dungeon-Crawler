from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks
from dungeoncrawler.status_effects import add_status_effect, temporal_lag_trigger


class Hooks(FloorHooks):
    """Temporal Lag and Haste Dysphoria mechanics for Floor 16."""

    def on_floor_start(self, state, floor):
        player = state.player
        if player:
            add_status_effect(player, "temporal_lag", 1)
            add_status_effect(player, "haste_dysphoria", 1)
            player._haste_dysphoria_base = player.speed

    def on_turn(self, state, floor):
        player = state.player
        if not player:
            return
        action = getattr(state.game, "last_action", None)
        cost = getattr(state.game, "last_cost", 0)
        temporal_lag_trigger(player, state, action, "stamina", cost)

    def use_anchor(self, state):
        player = state.player
        if not player:
            return False
        player.status_effects.pop("temporal_lag", None)
        if hasattr(state, "queue_message"):
            state.queue_message("The Anchor steadies time.")
        return True
