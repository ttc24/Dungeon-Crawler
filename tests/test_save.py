import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase


def test_load_missing_file(tmp_path, monkeypatch):
    missing_path = tmp_path / "save.json"
    monkeypatch.setattr(dungeon_module, 'SAVE_FILE', missing_path)

    dungeon = DungeonBase(1, 1)
    floor = dungeon.load_game()
    assert floor == 1


def test_load_corrupted_file(tmp_path, monkeypatch):
    corrupt_path = tmp_path / "save.json"
    corrupt_path.write_text("{bad json")
    monkeypatch.setattr(dungeon_module, 'SAVE_FILE', corrupt_path)

    dungeon = DungeonBase(1, 1)
    floor = dungeon.load_game()
    assert floor == 1
