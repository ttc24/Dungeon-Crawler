import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import main as main_module
from dungeoncrawler import constants
from dungeoncrawler import dungeon as dungeon_module


def test_tutorial_runs_only_once(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr(constants, 'SAVE_FILE', str(save_path))
    monkeypatch.setattr(dungeon_module, 'SAVE_FILE', str(save_path))

    # First run: new game
    inputs = iter(['n', 'Hero'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    calls = []

    def fake_tutorial(player):
        calls.append(player.name)

    monkeypatch.setattr(main_module, 'run_tutorial', fake_tutorial)

    def fake_play_game(self):
        if self.player is None:
            self.load_game()
        self.save_game(1)

    monkeypatch.setattr(main_module.DungeonBase, 'play_game', fake_play_game)

    main_module.main(args=[])

    assert calls == ['Hero']
    with open(save_path) as f:
        data = json.load(f)
    assert data.get('tutorial_complete') is True

    # Second run: load existing save, tutorial should not run
    inputs2 = iter(['y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs2))
    calls.clear()

    main_module.main(args=[])

    assert calls == []
