from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks
from dungeoncrawler.status_effects import add_status_effect


class Hooks(FloorHooks):
    """Blood Torrent and Compression Sickness mechanics for Floor 12."""

    def on_floor_start(self, state, floor):
        state.enemy_vision_bonus = 0

    def apply_blood_torrent(self, state):
        player = state.player
        if not player:
            return
        stacks = player.status_effects.get("blood_torrent", 0)
        player.status_effects["blood_torrent"] = min(3, stacks + 1)

    def trigger_compression_sickness(self, state):
        player = state.player
        if player:
            add_status_effect(player, "compression_sickness", 5)

    def on_turn(self, state, floor):
        player = state.player
        if not player:
            return
        stacks = player.status_effects.get("blood_torrent", 0)
        trail = player.status_effects.get("blood_scent", 0)
        state.enemy_vision_bonus = max(stacks, trail)
