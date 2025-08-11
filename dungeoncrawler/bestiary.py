"""Enemy and boss data loading utilities."""

from __future__ import annotations

import json
from pathlib import Path

from .items import Weapon

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_enemies():
    """Load enemy stats and abilities from ``enemies.json``."""
    path = DATA_DIR / "enemies.json"
    with open(path) as f:
        data = json.load(f)
    stats = {name: tuple(v["stats"]) for name, v in data.items()}
    abilities = {
        name: v.get("ability")
        for name, v in data.items()
        if v.get("ability")
    }
    return stats, abilities


def load_bosses():
    """Load boss stats and loot tables from ``bosses.json``."""
    path = DATA_DIR / "bosses.json"
    with open(path) as f:
        data = json.load(f)
    stats = {}
    loot = {}
    for name, cfg in data.items():
        hp, atk, dfs, gold = cfg["stats"]
        stats[name] = (hp, atk, dfs, gold, cfg.get("ability"))
        if "loot" in cfg:
            loot[name] = [Weapon(**item) for item in cfg["loot"]]
    return stats, loot


ENEMY_STATS, ENEMY_ABILITIES = load_enemies()
BOSS_STATS, BOSS_LOOT = load_bosses()
