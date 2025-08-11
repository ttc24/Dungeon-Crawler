import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def test_save_and_load(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr(dungeon_module, 'SAVE_FILE', str(save_path))

    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Saver")
    dungeon.player.gold = 42
    dungeon.save_game(floor=3)

    new_dungeon = DungeonBase(1, 1)
    floor = new_dungeon.load_game()
    assert floor == 3
    assert new_dungeon.player.name == "Saver"
    assert new_dungeon.player.gold == 42
