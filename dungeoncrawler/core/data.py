"""Utilities for loading core game data from JSON files."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@lru_cache(maxsize=None)
def load_enemies() -> Dict[str, Dict[str, Any]]:
    """Return enemy archetype definitions keyed by name."""
    path = DATA_DIR / "core_enemies.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {e["name"]: e for e in data.get("enemies", [])}


@lru_cache(maxsize=None)
def load_items() -> Dict[str, Dict[str, Any]]:
    """Return item definitions keyed by name."""
    path = DATA_DIR / "core_items.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {i["name"]: i for i in data.get("items", [])}


@lru_cache(maxsize=None)
def load_events() -> Dict[str, Any]:
    """Return event parameter definitions."""
    path = DATA_DIR / "core_events.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data
