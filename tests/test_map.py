import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.dungeon import DungeonBase, load_floor_configs
from dungeoncrawler.entities import Player


def test_render_map_snapshot():
    random.seed(0)
    load_floor_configs()
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    dungeon_map.generate_dungeon(game, floor=1)
    rendered = dungeon_map.render_map_string(game)
    expected = (
        "####################\n"
        "#########.##########\n"
        "########...#########\n"
        "#########.E.########\n"
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
    load_floor_configs()
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    dungeon_map.generate_dungeon(game, floor=1)

    # Simulate selecting "Show Map" from the menu
    game.handle_input("8")

    rendered = dungeon_map.render_map_string(game)

    assert "@" in rendered
    assert "." in rendered
    assert "#" in rendered
    assert "E" in rendered
    assert rendered.count("@") == 1
