from __future__ import annotations

from dungeoncrawler.dungeon import FloorHooks
from dungeoncrawler.status_effects import add_status_effect


class Hooks(FloorHooks):
    """Brood Bloom infections and Miasma Carrier aura for Floor 15."""

    def infect(self, entity, duration, spawn_callback):
        """Apply Brood Bloom to ``entity`` and register spawn callback."""
        entity.brood_spawn = spawn_callback
        entity.brood_bloom_stack = duration
        add_status_effect(entity, "brood_bloom", duration)

    def _protected(self, entity):
        trinket = getattr(entity, "trinket", None)
        if trinket and getattr(trinket, "name", "") == "Suppression Ring":
            return True
        inventory = list(getattr(entity, "inventory", []))
        for item in inventory:
            name = getattr(item, "name", "")
            if name in {"Filter Mask", "Air Filter"}:
                entity.inventory.remove(item)
                return True
        return False

    def on_turn(self, state, floor):
        game = state.game
        player = state.player
        if not player:
            return
        x, y = player.x, player.y
        if 0 <= y < game.height and 0 <= x < game.width:
            room = game.rooms[y][x]
            if room == "Miasma Carrier":
                targets = [player] + getattr(player, "companions", [])
                for ent in targets:
                    if not self._protected(ent):
                        add_status_effect(ent, "miasma_aura", 2)
