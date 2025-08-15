import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase


def test_load_missing_file(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr(dungeon_module, "SAVE_FILE", str(save_path))
    dungeon = DungeonBase(1, 1)
    floor = dungeon.load_game()
    assert floor == 1


def test_load_corrupt_file(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    save_path.write_text("{")
    monkeypatch.setattr(dungeon_module, "SAVE_FILE", str(save_path))
    dungeon = DungeonBase(1, 1)
    floor = dungeon.load_game()
    assert floor == 1
