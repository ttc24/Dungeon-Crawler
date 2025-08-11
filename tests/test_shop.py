import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def test_shop_purchase(monkeypatch):
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Buyer")
    dungeon.player.gold = 20
    monkeypatch.setattr('builtins.input', lambda _: '1')
    dungeon.shop()
    assert dungeon.player.gold == 10
    assert any(item.name == 'Health Potion' for item in dungeon.player.inventory)
