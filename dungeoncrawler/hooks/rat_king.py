import random

from dungeoncrawler.dungeon import FloorHooks
from dungeoncrawler.entities import Enemy


class Hooks(FloorHooks):
    """Special behaviour for the Rat King boss."""

    def __init__(self) -> None:
        self.exit_location = None

    def on_floor_start(self, state, floor):
        """Seal the exit until the Rat King falls."""
        game = state.game
        if game.exit_coords:
            self.exit_location = game.exit_coords
            ex, ey = game.exit_coords
            game.rooms[ey][ex] = None
            game.exit_coords = None

    def on_turn(self, state, floor):
        """Spawn spectral rats each turn unless the boss is stunned."""
        game = state.game
        boss = None
        for y, row in enumerate(game.rooms):
            for x, obj in enumerate(row):
                if isinstance(obj, Enemy) and obj.name == "Rat King":
                    boss = obj
                    break
            if boss:
                break
        if not boss or "stun" in boss.status_effects:
            return

        # Find empty adjacent tiles around the boss
        positions = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = boss.x + dx, boss.y + dy
            if 0 <= nx < game.width and 0 <= ny < game.height and game.rooms[ny][nx] is None:
                positions.append((nx, ny))
        if not positions:
            return

        nx, ny = random.choice(positions)
        stats = game.enemy_stats.get("Spectral Rat")
        if not stats:
            return
        hp_min, hp_max, atk_min, atk_max, defense = stats
        enemy = Enemy(
            "Spectral Rat",
            random.randint(hp_min, hp_max),
            random.randint(atk_min, atk_max),
            defense,
            0,
            ability=game.enemy_abilities.get("Spectral Rat"),
            ai=None,
            traits=game.enemy_traits.get("Spectral Rat"),
        )
        enemy.x, enemy.y = nx, ny
        game.rooms[ny][nx] = enemy

    def on_objective_check(self, state, floor):
        """Open the exit once the Rat King has been defeated."""
        game = state.game
        for y, row in enumerate(game.rooms):
            for x, obj in enumerate(row):
                if isinstance(obj, Enemy) and obj.name == "Rat King":
                    return False
        if self.exit_location and game.exit_coords is None:
            ex, ey = self.exit_location
            game.rooms[ey][ex] = "Exit"
            game.exit_coords = (ex, ey)
        return False
