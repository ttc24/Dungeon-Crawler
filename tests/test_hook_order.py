from dungeoncrawler import data
from dungeoncrawler.dungeon import DungeonBase, FloorHooks
from dungeoncrawler.entities import Player


class LoggingHooks(FloorHooks):
    def __init__(self, log):
        self.log = log

    def on_floor_start(self, state, floor):
        self.log.append("start")

    def on_turn(self, state, floor):
        self.log.append("turn")

    def on_objective_check(self, state, floor):
        self.log.append("objective")
        return True

    def on_floor_end(self, state, floor):
        self.log.append("end")


def test_hooks_execute_in_correct_order():
    data.load_floor_definitions()
    game = DungeonBase(5, 5)
    game.player = Player("hero")
    game.floor_def = data.get_floor(1)
    log = []
    game.floor_hooks = [LoggingHooks(log)]

    state = game._make_state(1)
    for hook in game.floor_hooks:
        hook.on_floor_start(state, game.floor_def)

    floor, continue_floor = game.process_turn(1)
    assert continue_floor is False

    end_state = game._make_state(floor - 1)
    for hook in game.floor_hooks:
        hook.on_floor_end(end_state, game.floor_def)

    assert log == ["start", "turn", "objective", "end"]
