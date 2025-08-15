from dungeoncrawler.dungeon import FloorHooks


class Hooks(FloorHooks):
    """Hazard dealing damage when standing on a gas vent."""

    def on_turn(self, state, floor):
        game = state.game
        player = state.player
        if not player:
            return
        x, y = player.x, player.y
        if 0 <= y < game.height and 0 <= x < game.width:
            if game.rooms[y][x] == "Gas Vent":
                player.take_damage(5, source="Gas Vent")
                state.queue_message("A gas vent spews noxious fumes!")
