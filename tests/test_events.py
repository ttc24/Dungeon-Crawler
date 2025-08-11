import os
import sys
from unittest.mock import patch
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.events import MerchantEvent, PuzzleEvent, TrapEvent


def setup_game():
    game = DungeonBase(5, 5)
    game.player = Player("hero")
    return game


def test_merchant_event_calls_shop():
    game = setup_game()
    event = MerchantEvent()
    with patch.object(DungeonBase, "shop") as mock_shop:
        event.trigger(game)
        assert mock_shop.called


def test_puzzle_event_rewards_on_correct_answer():
    game = setup_game()
    event = PuzzleEvent()
    with patch("dungeoncrawler.events.random.choice", return_value=("riddle", "answer")), \
         patch("builtins.input", return_value="answer"):
        gold_before = game.player.gold
        event.trigger(game)
        assert game.player.gold == gold_before + 50


def test_trap_event_deals_damage():
    game = setup_game()
    event = TrapEvent()
    with patch("dungeoncrawler.events.random.randint", return_value=10):
        health_before = game.player.health
        event.trigger(game)
        assert game.player.health == health_before - 10


def test_random_event_selection_from_floor_config():
    game = setup_game()
    with patch("dungeoncrawler.dungeon.random.choice", return_value=MerchantEvent), \
         patch.object(DungeonBase, "shop") as mock_shop:
        game.trigger_random_event(1)
        assert mock_shop.called
