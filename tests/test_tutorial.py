import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler import tutorial as tutorial_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.main import main


def test_tutorial_runs_once_per_save(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr(dungeon_module, "SAVE_FILE", str(save_path))
    run_file = tmp_path / "run.json"
    monkeypatch.setattr("dungeoncrawler.constants.RUN_FILE", run_file)
    monkeypatch.setattr("dungeoncrawler.dungeon.RUN_FILE", run_file)
    monkeypatch.setattr("dungeoncrawler.main.RUN_FILE", run_file)

    calls = []

    def fake_tutorial(game):
        calls.append(True)
        game.tutorial_complete = True

    monkeypatch.setattr(tutorial_module, "run", fake_tutorial)

    def fake_play_game(self):
        if self.player is None:
            self.load_game()
        self.save_game(1)

    monkeypatch.setattr(DungeonBase, "play_game", fake_play_game)

    inputs = iter(["n", "n", "Alice"])
    main([], input_func=lambda _: next(inputs), output_func=lambda _msg: None)
    assert len(calls) == 1

    inputs = iter(["n", "y"])
    main([], input_func=lambda _: next(inputs), output_func=lambda _msg: None)
    assert len(calls) == 1


def test_tutorial_runs_when_missing(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr(dungeon_module, "SAVE_FILE", str(save_path))
    run_file = tmp_path / "run.json"
    monkeypatch.setattr("dungeoncrawler.constants.RUN_FILE", run_file)
    monkeypatch.setattr("dungeoncrawler.dungeon.RUN_FILE", run_file)
    monkeypatch.setattr("dungeoncrawler.main.RUN_FILE", run_file)

    game = DungeonBase(80, 24)
    game.player = Player("Hero")
    game.tutorial_complete = False
    game.save_game(1)

    calls = []

    def fake_tutorial(game):
        calls.append(True)
        game.tutorial_complete = True

    monkeypatch.setattr(tutorial_module, "run", fake_tutorial)

    def fake_play_game(self):
        pass

    monkeypatch.setattr(DungeonBase, "play_game", fake_play_game)

    inputs = iter(["n", "y"])
    main([], input_func=lambda _: next(inputs), output_func=lambda _msg: None)
    assert len(calls) == 1
