from collections import deque

from hypothesis import given, settings
from hypothesis import strategies as st

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.data import load_floor_definitions
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Enemy, Player
from dungeoncrawler.events import BaseEvent


@settings(deadline=None)
@given(
    seed=st.integers(min_value=0, max_value=2**32 - 1), floor=st.integers(min_value=1, max_value=18)
)
def test_generation_properties(seed, floor):
    load_floor_definitions()
    dungeon = DungeonBase(1, 1, seed=seed)
    dungeon.player = Player("Tester")
    dungeon_map.generate_dungeon(dungeon, floor)

    start = (dungeon.player.x, dungeon.player.y)
    width, height = dungeon.width, dungeon.height

    visited = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if dungeon.rooms[ny][nx] is not None and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    carved = {
        (x, y) for y in range(height) for x in range(width) if dungeon.rooms[y][x] is not None
    }
    assert visited == carved
    assert dungeon.exit_coords in visited

    bosses = [
        obj
        for row in dungeon.rooms
        for obj in row
        if isinstance(obj, Enemy) and obj.name in dungeon.boss_stats
    ]
    expected_bosses = dungeon.floor_configs[floor].get("boss_slots", 1)
    assert len(bosses) == expected_bosses

    events = [obj for row in dungeon.rooms for obj in row if isinstance(obj, BaseEvent)]
    expected_events = 2 if floor == 1 else 1
    assert len(events) == expected_events

    total_xp = sum(obj.xp for row in dungeon.rooms for obj in row if isinstance(obj, Enemy))
    assert total_xp <= dungeon.width * dungeon.height * 2
