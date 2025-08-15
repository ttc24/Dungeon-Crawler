import random

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.data import get_floor, load_floor_definitions
from dungeoncrawler.dungeon import DungeonBase, load_hook_modules
from dungeoncrawler.entities import Enemy, Player
from dungeoncrawler.events import CacheEvent, FountainEvent


def test_intro_floor_has_fountain_and_cache_near_spawn():
    random.seed(0)
    load_floor_definitions()
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    dungeon_map.generate_dungeon(game, floor=1)

    px, py = game.player.x, game.player.y
    fountain = cache = None
    for y, row in enumerate(game.rooms):
        for x, obj in enumerate(row):
            if isinstance(obj, FountainEvent):
                fountain = (x, y)
            elif isinstance(obj, CacheEvent):
                cache = (x, y)
    assert fountain and cache
    assert abs(px - fountain[0]) + abs(py - fountain[1]) <= 10
    assert abs(px - cache[0]) + abs(py - cache[1]) <= 10


def test_rat_king_defeat_opens_exit():
    random.seed(0)
    load_floor_definitions()
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    dungeon_map.generate_dungeon(game, floor=1)

    floor_def = get_floor(1)
    hooks = load_hook_modules(floor_def.hooks)
    state = game._make_state(1)
    hook = hooks[0]
    hook.on_floor_start(state, floor_def)

    # Exit should be sealed at start
    assert game.exit_coords is None

    # Remove the Rat King to simulate defeat
    for y, row in enumerate(game.rooms):
        for x, obj in enumerate(row):
            if isinstance(obj, Enemy) and obj.name == "Rat King":
                game.rooms[y][x] = None
                break

    state = game._make_state(1)
    hook.on_objective_check(state, floor_def)
    ex, ey = hook.exit_location
    assert game.exit_coords == (ex, ey)
    assert game.rooms[ey][ex] == "Exit"
