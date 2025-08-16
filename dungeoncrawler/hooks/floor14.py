from __future__ import annotations

import random

from dungeoncrawler.dungeon import FloorHooks
from dungeoncrawler.status_effects import add_status_effect


class Hooks(FloorHooks):
    """Entropic Debt and Spiteful Reflection mechanics for Floor 14."""

    def on_floor_start(self, state, floor):
        player = state.player
        if player:
            # Apply Spiteful Reflection for the duration of the floor
            add_status_effect(player, "spiteful_reflection", 1)

    def on_turn(self, state, floor):
        player = state.player
        if not player:
            return
        action = getattr(state.game, "last_action", None)
        # Bitter cold chips away at the player each turn
        player.take_damage(1)
        if hasattr(state, "queue_message"):
            state.queue_message("The cold bites you for 1 damage.")
        # Slippery footing may waste move actions
        if action == "move" and random.random() < 0.2:
            if hasattr(state, "queue_message"):
                state.queue_message("You slip on the icy floor!")
            action = "wait"
        stacks = player.status_effects.get("entropic_debt", 0)
        if action in {"wait", "defend"}:
            # skipping or bracing repays two stacks
            stacks = max(0, stacks - 2)
            if stacks:
                player.status_effects["entropic_debt"] = stacks
            else:
                player.status_effects.pop("entropic_debt", None)
        else:
            player.status_effects["entropic_debt"] = min(10, stacks + 1)
        if hasattr(state.game, "last_action"):
            state.game.last_action = None

    def vent_to_totem(self, state):
        """Clear debt and possibly spawn an add. Returns True if an add spawns."""
        player = state.player
        if not player:
            return False
        had_debt = "entropic_debt" in player.status_effects
        player.status_effects.pop("entropic_debt", None)
        spawn = False
        if had_debt and random.random() < 0.5:
            spawn = True
            state.queue_message("An add materializes!" if hasattr(state, "queue_message") else "")
        return spawn
