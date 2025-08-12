import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import BOSS_LOOT, DungeonBase
from dungeoncrawler.entities import Enemy, Player


def test_boss_drops_loot(monkeypatch):
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    boss_name = next(iter(BOSS_LOOT))
    enemy = Enemy(boss_name, 1, 0, 0, 0)

    monkeypatch.setattr("builtins.input", lambda _: "1")
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    game.battle(enemy)

    assert BOSS_LOOT[boss_name][0] in game.player.inventory
