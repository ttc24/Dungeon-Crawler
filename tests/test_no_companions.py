import random

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.data import load_floor_definitions
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Companion, Player


def test_generate_dungeon_without_companion(monkeypatch):
    random.seed(0)
    load_floor_definitions()
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    monkeypatch.setattr(dungeon_map, "load_companions", lambda: [])
    dungeon_map.generate_dungeon(game, floor=1)
    assert all(
        not isinstance(tile, Companion)
        for row in game.rooms
        for tile in row
    )
