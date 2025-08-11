import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler import shop as shop_module


def setup_dungeon():
    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("hero")
    return dungeon


def test_floor_eight_event_grants_buff():
    dungeon = setup_dungeon()
    dungeon.trigger_floor_event(8)
    assert "inspire" in dungeon.player.status_effects


def test_floor_twelve_event_calls_shop():
    dungeon = setup_dungeon()
    with patch.object(shop_module, "shop") as mock_shop:
        dungeon.trigger_floor_event(12)
        assert mock_shop.called


def test_floor_fifteen_event_riddle_rewards_gold():
    dungeon = setup_dungeon()
    with patch("dungeoncrawler.dungeon.random.choice", return_value=("riddle", "answer")), \
         patch("builtins.input", return_value="answer"):
        gold_before = dungeon.player.gold
        dungeon.trigger_floor_event(15)
        assert dungeon.player.gold == gold_before + 50
