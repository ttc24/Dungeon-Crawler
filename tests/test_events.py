import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def setup_dungeon():
    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("hero")
    return dungeon


def test_merchant_event_calls_shop():
    dungeon = setup_dungeon()
    with patch("dungeoncrawler.dungeon.random.choice", return_value="Merchant"), \
         patch.object(DungeonBase, "shop") as mock_shop:
        dungeon.trigger_floor_event(4)
        assert mock_shop.called


def test_puzzle_event_rewards_gold():
    dungeon = setup_dungeon()
    riddle = {"question": "What has keys but can't open locks?", "answer": "piano"}
    with patch("dungeoncrawler.dungeon.random.choice", side_effect=["Puzzle", riddle]), \
         patch("builtins.input", return_value="piano"):
        gold_before = dungeon.player.gold
        dungeon.trigger_floor_event(4)
        assert dungeon.player.gold == gold_before + 50


def test_trap_event_deals_damage():
    dungeon = setup_dungeon()
    with patch("dungeoncrawler.dungeon.random.choice", return_value="Trap"):
        health_before = dungeon.player.health
        dungeon.trigger_floor_event(4)
        assert dungeon.player.health == health_before - 10
