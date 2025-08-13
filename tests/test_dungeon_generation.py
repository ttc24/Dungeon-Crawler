import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.dungeon import DungeonBase, load_floor_configs
from dungeoncrawler.entities import Enemy, Player
from dungeoncrawler.events import CacheEvent, FountainEvent


def test_generate_dungeon_size_and_population():
    random.seed(0)
    load_floor_configs()
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Tester")
    dungeon_map.generate_dungeon(dungeon, floor=1)

    assert dungeon.width == 20
    assert dungeon.height == 12
    assert len(dungeon.rooms) == dungeon.height
    assert all(len(row) == dungeon.width for row in dungeon.rooms)

    px, py = dungeon.player.x, dungeon.player.y
    assert dungeon.rooms[py][px] is dungeon.player

    ex, ey = dungeon.exit_coords
    assert dungeon.rooms[ey][ex] == "Exit"
    # Stairs should be close to the start on the first floor
    assert abs(px - ex) + abs(py - ey) <= 4

    # Early floors should always include helpful events
    assert any(isinstance(obj, FountainEvent) for row in dungeon.rooms for obj in row)
    assert any(isinstance(obj, CacheEvent) for row in dungeon.rooms for obj in row)

    enemy_count = sum(isinstance(obj, Enemy) for row in dungeon.rooms for obj in row)
    assert 3 <= enemy_count <= 5
