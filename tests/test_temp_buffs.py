from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.items import Item


class DummyDungeon(DungeonBase):
    def __init__(self):
        super().__init__(1, 1)
        self.player = Player("Tester")
        self.exit_coords = (0, 0)


def test_temp_buffs_reset_on_descend(monkeypatch):
    dungeon = DummyDungeon()
    dungeon.player.temp_strength = 2
    dungeon.player.temp_intelligence = 3
    dungeon.player.collect_item(Item("Key", ""))

    monkeypatch.setattr("builtins.input", lambda _: "y")
    dungeon.save_game = lambda f: None
    floor, cont = dungeon.check_floor_completion(1)

    assert (floor, cont) == (2, False)
    assert dungeon.player.temp_strength == 0
    assert dungeon.player.temp_intelligence == 0
