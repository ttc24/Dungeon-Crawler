import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.data import load_floor_definitions
from dungeoncrawler.entities import Player


def test_render_map_snapshot():
    random.seed(0)
    load_floor_definitions()
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    dungeon_map.generate_dungeon(game, floor=1)
    rendered = dungeon_map.render_map_string(game)
    expected = (
        "####################\n"
        "#########.##########\n"
        "########...#########\n"
        "#########...########\n"
        "#########....#######\n"
        "#########.##..######\n"
        "#########.@#...#####\n"
        "#########.......####\n"
        "#######........#####\n"
        "#########.....######\n"
        "##########...#######\n"
        "##########..########"
    )
    assert rendered == expected


def test_render_map_symbols_after_show_map():
    random.seed(0)
    load_floor_definitions()
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    dungeon_map.generate_dungeon(game, floor=1)

    # Simulate selecting "Show Map" from the menu
    game.handle_input("8")

    rendered = dungeon_map.render_map_string(game)

    assert "@" in rendered
    assert "." in rendered
    assert "#" in rendered
    assert rendered.count("@") == 1


def test_map_legend_toggle():
    random.seed(0)
    load_floor_definitions()
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    dungeon_map.generate_dungeon(game, floor=1)

    inputs = iter(["?", "?", "x"])
    game.view_map(input_func=lambda _: next(inputs))

    legend_entries = [
        "Legend:",
        " @ - You",
        " E - Exit",
        " . - Floor",
        " · - Discovered",
        " # - Unexplored",
    ]
    for entry in legend_entries:
        assert entry in game.renderer.lines
    assert game.renderer.lines.count("Legend:") == 1
    assert not game.renderer.legend_visible
