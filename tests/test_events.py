import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.events import (
    FountainEvent,
    MerchantEvent,
    PuzzleEvent,
    TrapEvent,
)
from dungeoncrawler.data import load_floor_definitions


def setup_game():
    load_floor_definitions()
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
    with patch("dungeoncrawler.events.random.choice", return_value=("riddle", "answer")):
        gold_before = game.player.gold
        event.trigger(
            game,
            input_func=lambda _: "answer",
            output_func=lambda _msg: None,
        )
        assert game.player.gold == gold_before + 50


def test_puzzle_event_handles_no_riddles():
    """Ensure the puzzle event gracefully handles an empty riddle list."""
    game = setup_game()
    game.riddles = []
    event = PuzzleEvent()
    # ``random.choice`` would raise IndexError if called; patch to track usage.
    with patch("dungeoncrawler.events.random.choice") as mock_choice:
        event.trigger(
            game,
            input_func=lambda _: "anything",
            output_func=lambda _msg: None,
        )
    # The event should exit early without attempting to select a riddle.
    mock_choice.assert_not_called()


def test_trap_event_deals_damage():
    game = setup_game()
    event = TrapEvent()
    with (
        patch("dungeoncrawler.events.random.randint", return_value=10),
        patch(
            "dungeoncrawler.events.random.random",
            side_effect=[0.99, 0.99],
        ),
    ):
        health_before = game.player.health
        event.trigger(game)
        assert game.player.health == health_before - 10


def test_trap_event_detect_and_disarm():
    game = setup_game()
    event = TrapEvent()
    stamina_before = game.player.stamina
    health_before = game.player.health
    with patch("dungeoncrawler.events.random.random", return_value=0.0):
        event.trigger(
            game,
            input_func=lambda _: "d",
            output_func=lambda _msg: None,
        )
    assert game.player.stamina == stamina_before - 15
    assert game.player.health == health_before


def test_fountain_event_drink_heals():
    game = setup_game()
    game.player.health = 50
    event = FountainEvent()
    inputs = iter(["d", "x"])
    with (
        patch("dungeoncrawler.events.random.randint", return_value=8),
        patch("dungeoncrawler.events.random.random", return_value=0.5),
    ):
        event.trigger(
            game,
            input_func=lambda _: next(inputs),
            output_func=lambda _msg: None,
        )
    assert game.player.health == 58
    assert event.remaining_uses == 1


def test_fountain_event_bottle_adds_item():
    game = setup_game()
    event = FountainEvent()
    inputs = iter(["b", "x"])
    event.trigger(
        game,
        input_func=lambda _: next(inputs),
        output_func=lambda _msg: None,
    )
    assert any(item.name == "Fountain Water" for item in game.player.inventory)
    assert event.remaining_uses == 1


def test_fountain_event_q_leaves_untouched():
    game = setup_game()
    game.player.health = 50
    event = FountainEvent()
    event.trigger(
        game,
        input_func=lambda _: "q",
        output_func=lambda _msg: None,
    )
    assert game.player.health == 50
    assert event.remaining_uses == 2


def test_random_event_selection_from_floor_config():
    game = setup_game()
    with (
        patch("dungeoncrawler.dungeon.random.choice", return_value=MerchantEvent),
        patch.object(DungeonBase, "shop") as mock_shop,
    ):
        game.trigger_random_event(1)
        assert mock_shop.called
