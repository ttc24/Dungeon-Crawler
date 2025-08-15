import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Enemy, Player
from dungeoncrawler.items import Item
from dungeoncrawler.hooks import warden_statue


def test_warden_statue_rotates_immunity_and_checks_sigils():
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    boss = Enemy("Warden Statue", 10, 1, 0, 0)
    boss.x = boss.y = 0
    game.rooms = [[boss]]

    hook = warden_statue.Hooks()
    state = game._make_state(1)

    hook.on_turn(state, None)
    assert boss.current_immunity == "physical"
    hook.on_turn(state, None)
    assert boss.current_immunity == "fire"
    hook.on_turn(state, None)
    assert boss.current_immunity == "ice"

    player = game.player
    player.inventory = [Item("Sigil", ""), Item("Sigil", ""), Item("Sigil", "")]
    state = game._make_state(1)
    assert hook.on_objective_check(state, None) is True
