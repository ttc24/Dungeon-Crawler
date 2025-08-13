"""Map raw keystrokes to high level action enums."""

from __future__ import annotations

from enum import Enum, auto


class Action(Enum):
    """Enumeration of high level player actions."""

    MOVE_W = auto()
    MOVE_E = auto()
    MOVE_N = auto()
    MOVE_S = auto()
    DEFEND = auto()
    USE_ITEM = auto()
    SHOW_MAP = auto()
    SHOW_STATUS = auto()
    SHOW_HELP = auto()
    QUIT = auto()
    UNKNOWN = auto()


# Default key bindings for a minimal terminal interface.  These bindings are
# intentionally tiny – front ends are free to provide their own mapping layer if
# required.
KEY_BINDINGS = {
    "1": Action.MOVE_W,
    "2": Action.MOVE_E,
    "3": Action.MOVE_N,
    "4": Action.MOVE_S,
    "5": Action.DEFEND,
    "6": Action.USE_ITEM,
    "7": Action.SHOW_MAP,
    "8": Action.SHOW_STATUS,
    "?": Action.SHOW_HELP,
    "q": Action.QUIT,
}


def get_action(key: str) -> Action:
    """Return the :class:`Action` associated with ``key``.

    Unrecognised keys return :data:`Action.UNKNOWN` which allows callers to
    handle invalid input consistently.
    """

    return KEY_BINDINGS.get(key, Action.UNKNOWN)


__all__ = ["Action", "get_action", "KEY_BINDINGS"]
