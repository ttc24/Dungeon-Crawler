from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks
from dungeoncrawler.status_effects import add_status_effect, clear_soul_tax


class Hooks(FloorHooks):
    """Fester Mark and Soul Tax mechanics for Floor 17."""

    def on_floor_start(self, state, floor):
        player = state.player
        if player:
            player.fester_mark_active = True
            player._soul_tax_state = state
            player._soul_tax_timers = []
            player._soul_tax_base_loot = state.config.loot_mult
        self.prev_enemy_count = len(getattr(state, "enemies", []))

    def on_turn(self, state, floor):
        player = state.player
        if not player:
            return
        enemies = getattr(state, "enemies", [])
        prev = getattr(self, "prev_enemy_count", 0)
        kills = max(0, prev - len(enemies))
        for _ in range(kills):
            add_status_effect(player, "soul_tax", 10)
            timers = getattr(player, "_soul_tax_timers", [])
            timers.append(10)
            player._soul_tax_timers = timers
            player.attack_power -= 1
            state.config.loot_mult += 0.05
        self.prev_enemy_count = len(enemies)

    def on_floor_end(self, state, floor):
        player = state.player
        if player:
            player.fester_mark_active = False
            clear_soul_tax(player)
            player.__dict__.pop("_soul_tax_state", None)
