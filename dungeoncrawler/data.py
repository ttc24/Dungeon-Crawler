"""Utilities for loading game data from JSON files."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

from .entities import Companion
from .events import (
    BaseEvent,
    CacheEvent,
    EscortMissionEvent,
    FountainEvent,
    HazardEvent,
    LoreNoteEvent,
    MerchantEvent,
    MiniQuestHookEvent,
    PuzzleChamberEvent,
    PuzzleEvent,
    ShrineEvent,
    ShrineGauntletEvent,
    TrapEvent,
)
from .items import Armor, Item, Trinket, Weapon

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

EVENT_CLASS_MAP = {
    cls.__name__: cls
    for cls in [
        MerchantEvent,
        PuzzleEvent,
        TrapEvent,
        FountainEvent,
        CacheEvent,
        LoreNoteEvent,
        ShrineEvent,
        MiniQuestHookEvent,
        HazardEvent,
        ShrineGauntletEvent,
        PuzzleChamberEvent,
        EscortMissionEvent,
    ]
}


@lru_cache(maxsize=None)
def load_items() -> Tuple[List[Item], List[Item]]:
    """Load shop and rare loot items from ``items.json``."""
    path = DATA_DIR / "items.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    def make(cfg: Dict) -> Item:
        t = cfg.get("type")
        if t == "Weapon":
            return Weapon(
                cfg["name"],
                cfg.get("description", ""),
                cfg.get("min_damage", 0),
                cfg.get("max_damage", 0),
                cfg.get("price", 0),
                cfg.get("rarity", "common"),
                cfg.get("effect"),
            )
        if t == "Armor":
            return Armor(
                cfg["name"],
                cfg.get("description", ""),
                cfg.get("defense", 0),
                cfg.get("price", 0),
                cfg.get("rarity", "common"),
                cfg.get("effect"),
            )
        if t == "Trinket":
            return Trinket(
                cfg["name"],
                cfg.get("description", ""),
                cfg.get("effect"),
                cfg.get("price", 0),
                cfg.get("rarity", "common"),
            )
        return Item(cfg["name"], cfg.get("description", ""))

    shop = [make(cfg) for cfg in data.get("shop", [])]
    rare = [make(cfg) for cfg in data.get("rare", [])]
    return shop, rare


@lru_cache(maxsize=None)
def load_companions() -> List[Companion]:
    """Load companion definitions from ``companions.json``."""
    path = DATA_DIR / "companions.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [Companion(**cfg) for cfg in data]


@lru_cache(maxsize=None)
def load_event_defs() -> (
    Tuple[List[type[BaseEvent]], List[float], Dict[str, int], List[type[BaseEvent]]]
):
    """Load event definitions including signature encounters."""
    path = DATA_DIR / "events_extended.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    events: List[type[BaseEvent]] = []
    weights: List[float] = []
    for name, weight in data.get("random", {}).items():
        cls = EVENT_CLASS_MAP.get(name)
        if cls:
            events.append(cls)
            weights.append(weight)

    signature: List[type[BaseEvent]] = []
    for name in data.get("signature", []):
        cls = EVENT_CLASS_MAP.get(name)
        if cls:
            signature.append(cls)

    dungeon_events: Dict[str, int] = data.get("dungeon", {})
    return events, weights, dungeon_events, signature
