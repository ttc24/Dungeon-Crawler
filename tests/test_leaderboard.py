import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def test_record_score_persistence(tmp_path, monkeypatch):
    score_path = tmp_path / "scores.json"
    monkeypatch.setattr(dungeon_module, "SCORE_FILE", str(score_path))

    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Tester")
    dungeon.run_start = 1
    dungeon.seed = 1234
    monkeypatch.setattr(dungeon_module.time, "time", lambda: 11)

    dungeon.record_score(5)
    data = json.loads(score_path.read_text())
    assert data[0]["player_name"] == "Tester"
    assert data[0]["floor_reached"] == 5
    assert data[0]["seed"] == 1234
    assert data[0]["run_duration"] == 10
    assert "epitaph" in data[0]


def test_view_leaderboard_display(tmp_path, monkeypatch, capsys):
    score_path = tmp_path / "scores.json"
    records = [
        {
            "player_name": "Alice",
            "score": 100,
            "floor_reached": 4,
            "run_duration": 30,
            "seed": 42,
        }
    ]
    score_path.write_text(json.dumps(records))
    monkeypatch.setattr(dungeon_module, "SCORE_FILE", str(score_path))

    dungeon = DungeonBase(1, 1)
    dungeon.view_leaderboard()
    captured = capsys.readouterr()
    assert "Alice" in captured.out
    assert "Floor 4" in captured.out
    assert "Seed 42" in captured.out


def test_leaderboard_sorting(tmp_path, monkeypatch, capsys):
    score_path = tmp_path / "scores.json"
    records = [
        {
            "player_name": "Alice",
            "score": 100,
            "floor_reached": 4,
            "run_duration": 30,
            "seed": 42,
        },
        {
            "player_name": "Bob",
            "score": 80,
            "floor_reached": 6,
            "run_duration": 20,
            "seed": 43,
        },
    ]
    score_path.write_text(json.dumps(records))
    monkeypatch.setattr(dungeon_module, "SCORE_FILE", str(score_path))

    dungeon = DungeonBase(1, 1)

    dungeon.view_leaderboard(sort_by="depth")
    out = capsys.readouterr().out.splitlines()
    assert out[1].startswith("Bob")

    dungeon.view_leaderboard(sort_by="time")
    out = capsys.readouterr().out.splitlines()
    assert out[1].startswith("Bob")

    dungeon.view_leaderboard(sort_by="score")
    out = capsys.readouterr().out.splitlines()
    assert out[1].startswith("Alice")
