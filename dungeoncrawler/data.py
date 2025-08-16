"""Utilities for loading game data from JSON files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

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
    RaceUnlockEvent,
    ShrineEvent,
    ShrineGauntletEvent,
    TrapEvent,
)
from .items import Armor, Augment, Item, Trinket, Weapon

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
        RaceUnlockEvent,
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
        if t == "Augment":
            return Augment(
                cfg["name"],
                cfg.get("description", ""),
                cfg.get("attack_bonus", 0),
                cfg.get("health_penalty", 0),
                cfg.get("max_stacks", 1),
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


@dataclass
class FloorDefinition:
    """Representation of a dungeon floor loaded from JSON."""

    id: str
    name: str
    map: List[List[str]]
    rule_mods: Dict[str, Any]
    objective: Dict[str, Any]
    spawns: List[Dict[str, Any]]
    ui: Dict[str, Any]
    hooks: List[str] = field(default_factory=list)


@lru_cache(maxsize=None)
def load_floor_definitions() -> Dict[str, FloorDefinition]:
    """Parse all floor definition files from ``data/floors``.

    Returns a mapping of floor ID to :class:`FloorDefinition` objects.
    Results are cached to avoid repeated JSON parsing.
    """

    floors: Dict[str, FloorDefinition] = {}
    directory = DATA_DIR / "floors"
    for path in sorted(directory.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
        floor = FloorDefinition(
            id=str(cfg.get("id")),
            name=cfg.get("name", ""),
            map=cfg.get("map", []),
            rule_mods=cfg.get("rule_mods", {}),
            objective=cfg.get("objective", {}),
            spawns=cfg.get("spawns", []),
            ui=cfg.get("ui", {}),
            hooks=cfg.get("hooks", []),
        )
        floors[floor.id] = floor
    return floors


def get_floor(floor_id: int | str) -> FloorDefinition | None:
    """Return the :class:`FloorDefinition` for ``floor_id`` if available."""

    floors = load_floor_definitions()
    key = str(floor_id).zfill(2)
    return floors.get(key)
