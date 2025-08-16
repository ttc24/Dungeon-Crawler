from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Spotlight and Audience Fatigue mechanics for Floor 18."""

    def on_floor_start(self, state, floor):
        self.history: list[str] = []
        if state:
            state.spotlight_ping = None

    def on_turn(self, state, floor):
        player = state.player
        if not player:
            return
        # Spotlight ping tracking
        if "spotlight_ping" in player.status_effects:
            state.spotlight_ping = (getattr(player, "x", 0), getattr(player, "y", 0))
            enemies = getattr(state, "enemies", [])
            for enemy in enemies:
                if getattr(enemy, "rarity", "") == "elite":
                    base = getattr(enemy, "_spotlight_base", enemy.attack_power)
                    if not getattr(enemy, "_spotlight_buffed", False):
                        enemy._spotlight_base = base
                        enemy.attack_power = int(base * 1.1)
                        enemy._spotlight_buffed = True
        else:
            state.spotlight_ping = None
            enemies = getattr(state, "enemies", [])
            for enemy in enemies:
                if getattr(enemy, "_spotlight_buffed", False):
                    enemy.attack_power = getattr(enemy, "_spotlight_base", enemy.attack_power)
                    enemy._spotlight_buffed = False
        # Audience Fatigue tracking
        action = getattr(state.game, "last_action", None)
        if action:
            history = self.history
            history.append(action)
            if len(history) > 5:
                history.pop(0)
            if history.count(action) >= 3:
                timers = getattr(player, "_audience_fatigue_timers", [])
                if len(timers) < 4:
                    timers.append(3)
                    player._audience_fatigue_timers = timers
                    player.status_effects["audience_fatigue"] = len(timers)
        
    # Item hooks
    def use_jammer(self, state):
        player = state.player
        if not player:
            return False
        player.status_effects.pop("spotlight_ping", None)
        state.spotlight_ping = None
        for enemy in getattr(state, "enemies", []):
            if getattr(enemy, "_spotlight_buffed", False):
                enemy.attack_power = getattr(enemy, "_spotlight_base", enemy.attack_power)
                enemy._spotlight_buffed = False
        if hasattr(state, "queue_message"):
            state.queue_message("The signal jammer muffles your trail.")
        return True

    def use_stealth(self, state):
        player = state.player
        if not player:
            return False
        player.status_effects.pop("spotlight_ping", None)
        state.spotlight_ping = None
        if hasattr(state, "queue_message"):
            state.queue_message("You vanish into the shadows.")
        return True

    def use_rewrite(self, state):
        player = state.player
        if not player:
            return False
        player.status_effects.pop("audience_fatigue", None)
        player._audience_fatigue_timers = []
        if hasattr(state, "queue_message"):
            state.queue_message("The rewrite clears the audience's fatigue.")
        return True
