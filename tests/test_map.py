import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def test_render_map_snapshot():
    random.seed(0)
    game = DungeonBase(1, 1)
    game.player = Player("Tester")
    dungeon_map.generate_dungeon(game, floor=1)
    rendered = dungeon_map.render_map_string(game)
    expected = (
        "########\n"
        "########\n"
        "########\n"
        "########\n"
        "####@###\n"
        "###E####\n"
        "########\n"
        "########"
    )
    assert rendered == expected
