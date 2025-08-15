import json

import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def test_record_score_appends_with_timestamp(tmp_path, monkeypatch):
    score_path = tmp_path / "scores.json"
    monkeypatch.setattr(dungeon_module, "SCORE_FILE", score_path)

    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("One")
    dungeon.run_start = 1
    dungeon.seed = 123
    monkeypatch.setattr(dungeon_module.time, "time", lambda: 11)
    dungeon.record_score(3)

    dungeon.player = Player("Two")
    dungeon.run_start = 1
    monkeypatch.setattr(dungeon_module.time, "time", lambda: 21)
    dungeon.record_score(4)

    data = json.loads(score_path.read_text())
    assert len(data) == 2
    assert "timestamp" in data[0]
    assert data[1]["player_name"] == "Two"
