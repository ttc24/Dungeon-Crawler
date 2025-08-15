import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Enemy, Player
from dungeoncrawler.events import CacheEvent, FountainEvent
from dungeoncrawler.data import load_floor_definitions


def test_generate_dungeon_size_and_population():
    random.seed(0)
    load_floor_definitions()
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
    assert abs(px - ex) + abs(py - ey) <= 10

    # Early floors should always include a helpful event near the start
    events = [
        (obj, x, y)
        for y, row in enumerate(dungeon.rooms)
        for x, obj in enumerate(row)
        if isinstance(obj, (FountainEvent, CacheEvent))
    ]
    assert events
    ev_obj, ev_x, ev_y = events[0]
    assert abs(px - ev_x) + abs(py - ev_y) <= 10

    enemy_count = sum(isinstance(obj, Enemy) for row in dungeon.rooms for obj in row)
    assert 3 <= enemy_count <= 5


def test_generate_dungeon_scaling_and_spawn_features_floor2():
    random.seed(0)
    load_floor_definitions()
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Tester")
    dungeon_map.generate_dungeon(dungeon, floor=2)

    assert dungeon.width == 24
    assert dungeon.height == 14

    px, py = dungeon.player.x, dungeon.player.y
    ex, ey = dungeon.exit_coords
    assert abs(px - ex) + abs(py - ey) <= 10

    events = [
        (obj, x, y)
        for y, row in enumerate(dungeon.rooms)
        for x, obj in enumerate(row)
        if isinstance(obj, (FountainEvent, CacheEvent))
    ]
    assert events
    ev_obj, ev_x, ev_y = events[0]
    assert abs(px - ev_x) + abs(py - ev_y) <= 10
