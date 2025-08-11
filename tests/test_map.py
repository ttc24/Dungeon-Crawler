import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.map import MapRenderer


def build_sample_dungeon():
    dungeon = DungeonBase(3, 3)
    dungeon.rooms = [["Empty" for _ in range(3)] for _ in range(3)]
    dungeon.player = Player("Tester")
    dungeon.player.x = 1
    dungeon.player.y = 1
    dungeon.rooms[1][1] = dungeon.player
    dungeon.visited_rooms = {(1, 1), (1, 2)}
    dungeon.exit_coords = (2, 2)
    return dungeon


def test_render_map_string_snapshot():
    dungeon = build_sample_dungeon()
    renderer = MapRenderer(dungeon)
    rendered = renderer.render_to_string()

    expected = (
        "\x1b[90m#\x1b[0m\x1b[90m#\x1b[0m\x1b[90m#\x1b[0m\n"
        "\x1b[90m#\x1b[0m\x1b[36m@\x1b[0m\x1b[90m#\x1b[0m\n"
        "\x1b[90m#\x1b[0m\x1b[37m.\x1b[0m\x1b[35mE\x1b[0m"
    )

    assert rendered == expected


def test_render_map_with_legend_snapshot():
    dungeon = build_sample_dungeon()
    renderer = MapRenderer(dungeon)
    rendered = renderer.render_to_string(show_legend=True)

    expected = (
        "\x1b[90m#\x1b[0m\x1b[90m#\x1b[0m\x1b[90m#\x1b[0m\n"
        "\x1b[90m#\x1b[0m\x1b[36m@\x1b[0m\x1b[90m#\x1b[0m\n"
        "\x1b[90m#\x1b[0m\x1b[37m.\x1b[0m\x1b[35mE\x1b[0m\n\n"
        "\x1b[36m@\x1b[0m - Player\n"
        "\x1b[37m.\x1b[0m - Visited\n"
        "\x1b[90m#\x1b[0m - Unseen\n"
        "\x1b[35mE\x1b[0m - Exit"
    )

    assert rendered == expected

