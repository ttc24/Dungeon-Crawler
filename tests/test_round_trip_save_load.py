import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json

import dungeoncrawler.constants as constants
import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def test_round_trip_save_load(tmp_path, monkeypatch):
    save_path = tmp_path / "savegame.json"
    monkeypatch.setattr(dungeon_module, "SAVE_FILE", str(save_path))
    monkeypatch.setattr(constants, "SAVE_FILE", str(save_path))

    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Hero")
    dungeon.player.gold = 99
    dungeon.save_game(floor=2)

    with open(save_path) as f:
        original_data = json.load(f)

    new_dungeon = DungeonBase(1, 1)
    floor = new_dungeon.load_game()
    new_dungeon.save_game(floor)

    with open(save_path) as f:
        round_trip_data = json.load(f)

    assert round_trip_data == original_data
