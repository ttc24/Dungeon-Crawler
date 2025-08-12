import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.items import Item


class DummyDungeon(DungeonBase):
    """Dungeon with small map avoiding heavy generation."""

    def __init__(self):
        super().__init__(1, 1)
        self.player = Player("Tester")
        self.exit_coords = (0, 0)


def test_handle_input_moves_player(monkeypatch):
    dungeon = DummyDungeon()
    called = {}

    def fake_move(direction):
        called["direction"] = direction

    dungeon.move_player = fake_move
    assert dungeon.handle_input("1") is True
    assert called["direction"] == "left"


def test_handle_input_quit():
    dungeon = DummyDungeon()
    assert dungeon.handle_input("7") is False


def test_process_turn_heals_and_calls_check(monkeypatch):
    dungeon = DummyDungeon()
    dungeon.player.level = 5
    dungeon.player.health = dungeon.player.max_health - 10

    def fake_check(floor):
        fake_check.called = True
        return floor, True

    dungeon.check_floor_completion = fake_check
    floor, cont = dungeon.process_turn(1)

    assert fake_check.called is True
    assert dungeon.player.health == dungeon.player.max_health - 9
    assert floor == 1 and cont is True


def test_check_floor_completion_proceed(monkeypatch):
    dungeon = DummyDungeon()
    dungeon.player.collect_item(Item("Key", ""))

    monkeypatch.setattr("builtins.input", lambda _: "y")
    saved = {}
    dungeon.save_game = lambda f: saved.setdefault("floor", f)

    floor, cont = dungeon.check_floor_completion(1)
    assert saved["floor"] == 2
    assert (floor, cont) == (2, False)


def test_check_floor_completion_exit(monkeypatch):
    dungeon = DummyDungeon()
    dungeon.player.collect_item(Item("Key", ""))

    monkeypatch.setattr("builtins.input", lambda _: "n")
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    recorded = {}
    dungeon.record_score = lambda f: recorded.setdefault("floor", f)

    floor, cont = dungeon.check_floor_completion(3)
    assert recorded["floor"] == 3
    assert (floor, cont) == (3, None)
