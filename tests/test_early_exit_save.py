import json
from pathlib import Path

import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.items import Item


def test_retire_removes_save_file(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    score_path = tmp_path / "scores.json"
    monkeypatch.setattr(dungeon_module, "SAVE_FILE", save_path)
    monkeypatch.setattr(dungeon_module, "SCORE_FILE", score_path)

    dungeon = DungeonBase(1, 1)
    player = Player("Tester")
    player.inventory.append(Item("Key", ""))
    dungeon.player = player
    dungeon.exit_coords = (0, 0)
    player.x = 0
    player.y = 0

    save_path.write_text("{}")

    monkeypatch.setattr("builtins.input", lambda _: "r")
    floor, status = dungeon.check_floor_completion(9)

    assert status is None
    assert not save_path.exists()
