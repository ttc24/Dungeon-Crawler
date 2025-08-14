import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.main import build_character
import json


def setup_dungeon():
    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("hero")
    dungeon.next_shop_floor = 99
    dungeon.next_shop_floor = 99
    return dungeon


def test_shops_spawn_every_few_floors():
    dungeon = setup_dungeon()
    dungeon.next_shop_floor = 2
    with (
        patch.object(DungeonBase, "shop") as mock_shop,
        patch("dungeoncrawler.dungeon.random.randint", return_value=2),
        patch.object(DungeonBase, "offer_guild", return_value=None),
        patch.object(DungeonBase, "offer_race", return_value=None),
        patch.object(DungeonBase, "_floor_four_event", return_value=None),
        patch.object(DungeonBase, "trigger_signature_event", return_value=None),
    ):
        dungeon.trigger_floor_event(2)
        assert mock_shop.call_count == 1
        assert dungeon.next_shop_floor == 4
        dungeon.trigger_floor_event(3)
        assert mock_shop.call_count == 1
        dungeon.trigger_floor_event(4)
        assert mock_shop.call_count == 2


def test_signature_event_triggers_once_per_floor():
    dungeon = setup_dungeon()

    class DummyEvent:
        call_count = 0

        def trigger(self, game, input_func=input, output_func=print):
            DummyEvent.call_count += 1

    dungeon.signature_events = [DummyEvent]

    with (
        patch.object(DungeonBase, "offer_class", return_value=None),
        patch.object(DungeonBase, "offer_guild", return_value=None),
        patch.object(DungeonBase, "offer_race", return_value=None),
    ):
        for floor in range(1, 16):
            dungeon.trigger_floor_event(floor)

    assert DummyEvent.call_count == 15


def test_floor_progression_unlocks_features():
    dungeon = setup_dungeon()

    class DummyEvent:
        def trigger(self, dungeon):
            pass

    called = {"class": False, "guild": False, "race": False}

    def fake_offer_class(self):
        called["class"] = True
        self.player.choose_class("Warrior")

    def fake_offer_guild(self):
        called["guild"] = True
        self.player.join_guild("Warriors' Guild")

    def fake_offer_race(self):
        called["race"] = True
        self.player.choose_race("Elf")

    with (
        patch("dungeoncrawler.dungeon.random.choice", return_value=DummyEvent),
        patch("dungeoncrawler.dungeon.random.randint", return_value=1),
        patch.object(DungeonBase, "offer_class", new=fake_offer_class),
        patch.object(DungeonBase, "offer_guild", new=fake_offer_guild),
        patch.object(DungeonBase, "offer_race", new=fake_offer_race),
    ):
        dungeon.trigger_floor_event(1)
        dungeon.trigger_floor_event(2)
        dungeon.trigger_floor_event(3)

    assert dungeon.player.class_type == "Warrior"
    assert dungeon.player.guild == "Warriors' Guild"
    assert dungeon.player.race == "Elf"
    assert called == {"class": True, "guild": True, "race": True}


def test_unlocks_persist_between_runs(tmp_path, monkeypatch):
    run_file = tmp_path / "run.json"
    monkeypatch.setattr("dungeoncrawler.constants.RUN_FILE", run_file)
    monkeypatch.setattr("dungeoncrawler.dungeon.RUN_FILE", run_file)
    monkeypatch.setattr("dungeoncrawler.main.RUN_FILE", run_file)

    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("hero")

    class DummyEvent:
        def trigger(self, game, input_func=None, output_func=None):
            return

    inputs = iter(["1", "1", "2"])  # class, guild, race choices
    with (
        patch("builtins.input", lambda _: next(inputs)),
        patch("dungeoncrawler.dungeon.random.choice", return_value=DummyEvent),
        patch("dungeoncrawler.dungeon.random.randint", return_value=1),
        patch.object(DungeonBase, "shop", lambda self, *a, **k: None),
    ):
        dungeon.trigger_floor_event(1)
        dungeon.trigger_floor_event(2)
        dungeon.trigger_floor_event(3)

    with open(run_file) as f:
        data = json.load(f)
    assert data["unlocks"] == {"class": True, "guild": True, "race": True}

    inputs = iter(["Bob", "1", "1", "2"])  # name, class, guild, race
    player = build_character(
        input_func=lambda _: next(inputs), output_func=lambda _msg: None
    )
    assert player.class_type == "Warrior"
    assert player.guild == "Warriors' Guild"
    assert player.race == "Elf"


def test_trigger_floor_event_calls_expected_handler():
    dungeon = setup_dungeon()
    floor_method_map = {
        1: "_floor_one_event",
        2: "_floor_two_event",
        3: "_floor_three_event",
        4: "_floor_four_event",
        5: "_floor_five_event",
        6: "_floor_six_event",
        7: "_floor_seven_event",
        8: "_floor_eight_event",
        9: "_floor_nine_event",
        10: "_floor_ten_event",
        11: "_floor_eleven_event",
        12: "_floor_twelve_event",
        13: "_floor_thirteen_event",
        14: "_floor_fourteen_event",
        15: "_floor_fifteen_event",
    }
    for floor, method in floor_method_map.items():
        called = False

        def stub(self):
            nonlocal called
            called = True

        with patch.object(DungeonBase, method, new=stub):
            dungeon.trigger_floor_event(floor)
            assert called, f"{method} not triggered for floor {floor}"
