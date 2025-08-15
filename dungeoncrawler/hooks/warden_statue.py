from itertools import cycle

from dungeoncrawler.dungeon import FloorHooks
from dungeoncrawler.entities import Enemy


class Hooks(FloorHooks):
    """Floor behaviour for the Warden Statue boss."""

    def __init__(self) -> None:
        self._cycle = cycle(["physical", "fire", "ice"])
        self.current_immunity = next(self._cycle)

    def _find_boss(self, game):
        for row in game.rooms:
            for obj in row:
                if isinstance(obj, Enemy) and obj.name == "Warden Statue":
                    return obj
        return None

    def on_turn(self, state, floor):
        boss = self._find_boss(state.game)
        if boss:
            boss.current_immunity = self.current_immunity
            self.current_immunity = next(self._cycle)

    def on_objective_check(self, state, floor):
        player = state.player
        count = sum(
            1 for item in getattr(player, "inventory", []) if getattr(item, "name", "") == "Sigil"
        )
        return count >= 3
