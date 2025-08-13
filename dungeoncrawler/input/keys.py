"""Keyboard mapping helpers."""

from __future__ import annotations

from enum import Enum, auto
from typing import Optional


class Action(Enum):
    """High level input actions understood by the game."""

    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    VISIT_SHOP = auto()
    INVENTORY = auto()
    QUIT = auto()
    SHOW_MAP = auto()
    LEADERBOARD = auto()


# Mapping of raw key presses to :class:`Action` values.
KEYMAP = {
    "1": Action.MOVE_LEFT,
    "2": Action.MOVE_RIGHT,
    "3": Action.MOVE_UP,
    "4": Action.MOVE_DOWN,
    "5": Action.VISIT_SHOP,
    "6": Action.INVENTORY,
    "7": Action.QUIT,
    "8": Action.SHOW_MAP,
    "?": Action.LEADERBOARD,
    "q": Action.QUIT,
}


# Reverse mapping used when passing legacy numeric choices to existing code.
CHOICE_MAP = {
    Action.MOVE_LEFT: "1",
    Action.MOVE_RIGHT: "2",
    Action.MOVE_UP: "3",
    Action.MOVE_DOWN: "4",
    Action.VISIT_SHOP: "5",
    Action.INVENTORY: "6",
    Action.QUIT: "7",
    Action.SHOW_MAP: "8",
    Action.LEADERBOARD: "9",
}


def get_action(key: str) -> Optional[Action]:
    """Return the :class:`Action` for ``key`` if one exists."""

    return KEYMAP.get(key)


def to_choice(action: Action) -> str:
    """Translate ``action`` back to the legacy numeric choice string."""

    return CHOICE_MAP[action]


def read_key(prompt: str = "") -> str:
    """Return a raw key press using ``input``.

    Wrapping ``input`` in this helper centralises keyboard access so that
    gameplay loops do not call ``input`` directly, making it easier to swap
    in alternative input mechanisms later on.
    """

    try:
        return input(prompt)
    except EOFError:
        # When running under tests there may be no stdin.  Returning an empty
        # string allows callers to handle the absence of input gracefully.
        return ""
