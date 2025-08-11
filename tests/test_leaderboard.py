import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def test_record_score_persistence(tmp_path, monkeypatch):
    score_path = tmp_path / "scores.json"
    monkeypatch.setattr(dungeon_module, 'SCORE_FILE', str(score_path))

    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Tester")

    dungeon.record_score(floor=3, run_duration=120, seed=42)

    with open(score_path) as f:
        data = json.load(f)

    assert len(data) == 1
    record = data[0]
    assert record["player_name"] == "Tester"
    assert record["floor_reached"] == 3
    assert record["run_duration"] == 120
    assert record["seed"] == 42


def test_view_leaderboard_displays(tmp_path, monkeypatch, capsys):
    score_path = tmp_path / "scores.json"
    records = [{
        "player_name": "Alice",
        "score": 50,
        "floor_reached": 2,
        "run_duration": 30,
        "seed": 7,
    }]
    with open(score_path, 'w') as f:
        json.dump(records, f)

    monkeypatch.setattr(dungeon_module, 'SCORE_FILE', str(score_path))

    dungeon = DungeonBase(1, 1)
    dungeon.view_leaderboard()

    captured = capsys.readouterr().out
    assert "Alice" in captured
    assert "50" in captured
    assert "Floor 2" in captured
    assert "Seed 7" in captured
