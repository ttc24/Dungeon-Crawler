"""Helpers for persisting and restoring game state."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Mapping, Optional, cast

from ..constants import SAVE_FILE

SCHEMA_VERSION = 1


def save_game(state: Mapping[str, Any] | object) -> None:
    """Persist ``state`` to :data:`SAVE_FILE` using JSON.

    The object is serialised using :func:`dataclasses.asdict` when applicable and
    wrapped together with a schema version number allowing future migrations.
    """

    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(state, Mapping):
        payload = dict(state)
    elif is_dataclass(state) and not isinstance(state, type):
        payload = cast(Dict[str, Any], asdict(state))
    else:
        raise TypeError("state must be a dataclass instance or mapping")

    data = {"version": SCHEMA_VERSION, "state": payload}
    with SAVE_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f)


def load_game() -> Optional[Dict[str, Any]]:
    """Return previously saved state if the schema version matches.

    ``None`` is returned when the file does not exist, is unreadable or the
    schema version is missing or outdated.
    """

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    if data.get("version") != SCHEMA_VERSION:
        return None

    state = data.get("state")
    if not isinstance(state, dict):
        return None
    return state
