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
    rendered = dungeon_map.render_map_string(game).replace(" ", "_")
    expected = (
        "____________________\n"
        "____________________\n"
        "____________________\n"
        "____________________\n"
        "_________.__________\n"
        "_________.__________\n"
        "_________.@_________\n"
        "_________...._______\n"
        "_________...________\n"
        "__________._________\n"
        "____________________\n"
        "____________________"
    )
    assert rendered == expected
