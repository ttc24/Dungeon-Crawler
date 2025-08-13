import pytest

from dungeoncrawler.input import keys


def test_key_to_action_mapping():
    assert keys.get_action("1") is keys.Action.MOVE_LEFT
    assert keys.get_action("8") is keys.Action.SHOW_MAP
    assert keys.get_action("q") is keys.Action.QUIT
    assert keys.get_action("?") is keys.Action.LEADERBOARD


def test_action_to_choice():
    assert keys.to_choice(keys.Action.SHOW_MAP) == "8"
    assert keys.to_choice(keys.Action.QUIT) == "7"


def test_read_key(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _=None: "?")
    assert keys.read_key("prompt") == "?"
