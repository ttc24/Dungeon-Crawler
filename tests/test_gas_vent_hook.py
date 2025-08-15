import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.hooks import gas_vent


def test_gas_vent_deals_damage_and_logs_message():
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    game.rooms = [["Gas Vent"]]
    game.player.x = game.player.y = 0
    hook = gas_vent.Hooks()
    state = game._make_state(1)
    hp_before = game.player.health
    hook.on_turn(state, None)
    assert game.player.health == hp_before - 5
    assert any("gas vent" in msg.lower() for msg in state.log)
