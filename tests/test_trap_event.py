from unittest.mock import Mock, patch

from dungeoncrawler.events import TrapEvent


def test_trap_event_disarm(game):
    event = TrapEvent()
    input_mock = Mock(return_value="d")
    output_mock = Mock()
    with patch("dungeoncrawler.events.random.random", return_value=0.0):
        event.trigger(game, input_func=input_mock, output_func=output_mock)
    assert game.player.stamina == 100 - event.disarm_cost
    output_mock.assert_any_call("You carefully disarm the trap.")
    assert (game.player.x, game.player.y) in game.visited_rooms


def test_trap_event_damage_and_bleed(game):
    event = TrapEvent()
    output_mock = Mock()
    with (
        patch("dungeoncrawler.events.random.randint", return_value=7),
        patch("dungeoncrawler.events.random.random", side_effect=[0.99, 0.0]),
    ):
        event.trigger(game, input_func=lambda _: "", output_func=output_mock)
    assert game.player.health == 100 - 7
    assert "bleed" in game.player.status_effects
    output_mock.assert_any_call("A trap is sprung! You take 7 damage.")
