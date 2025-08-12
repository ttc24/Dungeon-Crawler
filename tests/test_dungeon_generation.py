import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Enemy, Player


def test_generate_dungeon_size_and_population():
    random.seed(0)
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Tester")
    dungeon_map.generate_dungeon(dungeon, floor=1)

    assert dungeon.width == 8
    assert dungeon.height == 8
    assert len(dungeon.rooms) == dungeon.height
    assert all(len(row) == dungeon.width for row in dungeon.rooms)

    px, py = dungeon.player.x, dungeon.player.y
    assert dungeon.rooms[py][px] is dungeon.player

    ex, ey = dungeon.exit_coords
    assert dungeon.rooms[ey][ex] == "Exit"

    enemy_count = sum(isinstance(obj, Enemy) for row in dungeon.rooms for obj in row)
    assert enemy_count >= 6
