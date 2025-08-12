import importlib
import json
import logging
import pkgutil
from pathlib import Path

from .items import Item, Weapon

MODS_DIR = Path(__file__).resolve().parent.parent / "mods"


def discover_plugins():
    """Return imported plugin modules found under :mod:`mods` package."""
    if not MODS_DIR.exists():
        return []
    modules = []
    for m in pkgutil.iter_modules([str(MODS_DIR)]):
        try:
            modules.append(importlib.import_module(f"mods.{m.name}"))
        except ImportError:
            logging.warning("Failed to import plugin '%s'", m.name)
    return modules


def _load_json_from_mod(mod, filename):
    mod_path = Path(mod.__file__).parent
    json_path = mod_path / "data" / filename
    if json_path.exists():
        try:
            with open(json_path) as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None
    return None


def apply_enemy_plugins(enemy_stats, enemy_abilities, enemy_ai, enemy_traits):
    """Augment enemy dictionaries with contributions from mods."""
    for mod in discover_plugins():
        data = _load_json_from_mod(mod, "enemies.json")
        if data:
            for cfg in data:
                name = cfg["name"]
                enemy_stats[name] = tuple(cfg["stats"])
                ability = cfg.get("ability")
                if ability:
                    enemy_abilities[name] = ability
                if cfg.get("ai"):
                    enemy_ai[name] = cfg["ai"]
                if cfg.get("traits"):
                    enemy_traits[name] = cfg["traits"]
        if hasattr(mod, "register_enemies"):
            mod.register_enemies(enemy_stats, enemy_abilities)


def apply_item_plugins(shop_items):
    """Append new items to ``shop_items`` list via JSON or hooks."""
    for mod in discover_plugins():
        data = _load_json_from_mod(mod, "items.json")
        if data:
            for cfg in data.get("weapons", []):
                shop_items.append(Weapon(**cfg))
            for cfg in data.get("items", []):
                shop_items.append(Item(**cfg))
        if hasattr(mod, "register_items"):
            mod.register_items(shop_items)
