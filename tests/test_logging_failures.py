import logging
from json import JSONDecodeError

import dungeoncrawler.dungeon as dungeon_module
import dungeoncrawler.main as main_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def test_save_game_logs_and_informs_user(tmp_path, monkeypatch, caplog):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr(dungeon_module, "SAVE_FILE", save_path)
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Hero")

    messages = []
    monkeypatch.setattr(dungeon.renderer, "show_message", lambda msg: messages.append(msg))

    def _raise(*args, **kwargs):  # pragma: no cover - helper
        raise IOError("boom")

    monkeypatch.setattr("builtins.open", _raise)
    with caplog.at_level(logging.ERROR):
        dungeon.save_game(1)
    assert any("Failed to save game" in rec.getMessage() for rec in caplog.records)
    assert any("Failed to save game" in m for m in messages)


def test_save_run_stats_logs_and_informs_user(tmp_path, monkeypatch, caplog):
    run_path = tmp_path / "run.json"
    monkeypatch.setattr(dungeon_module, "RUN_FILE", run_path)
    dungeon = DungeonBase(1, 1)
    messages = []
    monkeypatch.setattr(dungeon.renderer, "show_message", lambda msg: messages.append(msg))

    def _raise(*args, **kwargs):  # pragma: no cover - helper
        raise IOError("boom")

    monkeypatch.setattr("builtins.open", _raise)
    with caplog.at_level(logging.ERROR):
        dungeon.save_run_stats()
    assert any("Failed to save run statistics" in rec.getMessage() for rec in caplog.records)
    assert any("Failed to update run statistics" in m for m in messages)


def test_load_unlocks_logs_on_failure(tmp_path, monkeypatch, caplog):
    run_path = tmp_path / "run.json"
    run_path.touch()
    monkeypatch.setattr(main_module, "RUN_FILE", run_path)

    def _raise(*args, **kwargs):  # pragma: no cover - helper
        raise IOError("boom")

    monkeypatch.setattr("builtins.open", _raise)
    with caplog.at_level(logging.ERROR):
        main_module._load_unlocks()
    assert any("Failed to load unlocks" in rec.getMessage() for rec in caplog.records)


def test_init_logs_when_run_stats_unreadable(tmp_path, monkeypatch, caplog):
    run_path = tmp_path / "run.json"
    run_path.write_text("{}")
    monkeypatch.setattr(dungeon_module, "RUN_FILE", run_path)

    original_open = open

    def fake_open(path, *args, **kwargs):  # pragma: no cover - helper
        if path == run_path:
            raise JSONDecodeError("boom", "", 0)
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)
    with caplog.at_level(logging.ERROR):
        DungeonBase(1, 1)
    assert any("Failed to load run statistics" in rec.getMessage() for rec in caplog.records)
