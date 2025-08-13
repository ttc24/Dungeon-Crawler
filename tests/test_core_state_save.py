from dataclasses import asdict

import dungeoncrawler.core.save as save_module
from dungeoncrawler.core.map import GameMap
from dungeoncrawler.core.state import GameState


def test_save_and_load_gamestate(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr(save_module, "SAVE_FILE", save_path)
    state = GameState(
        seed=42, current_floor=3, player=None, game_map=GameMap([[1]]), log=["hello", "world"]
    )
    save_module.save_game(state)
    loaded = save_module.load_game()
    assert loaded == asdict(state)
