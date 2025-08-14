import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def setup_dungeon():
    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("hero")
    dungeon.next_shop_floor = 99
    return dungeon


def test_floor_eight_event_grants_buff():
    dungeon = setup_dungeon()
    dungeon.trigger_floor_event(8)
    assert "inspire" in dungeon.player.status_effects


def test_shops_spawn_every_few_floors():
    dungeon = setup_dungeon()
    dungeon.next_shop_floor = 2
    with (
        patch.object(DungeonBase, "shop") as mock_shop,
        patch("dungeoncrawler.dungeon.random.randint", return_value=2),
        patch.object(DungeonBase, "offer_guild", return_value=None),
        patch.object(DungeonBase, "offer_race", return_value=None),
        patch.object(DungeonBase, "_floor_four_event", return_value=None),
    ):
        dungeon.trigger_floor_event(2)
        assert mock_shop.call_count == 1
        assert dungeon.next_shop_floor == 4
        dungeon.trigger_floor_event(3)
        assert mock_shop.call_count == 1
        dungeon.trigger_floor_event(4)
        assert mock_shop.call_count == 2


def test_floor_fifteen_event_riddle_rewards_gold():
    dungeon = setup_dungeon()
    with (
        patch("dungeoncrawler.dungeon.random.choice", return_value=("riddle", "answer")),
        patch("builtins.input", return_value="answer"),
    ):
        gold_before = dungeon.player.gold
        dungeon.trigger_floor_event(15)
        assert dungeon.player.gold == gold_before + 50


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
