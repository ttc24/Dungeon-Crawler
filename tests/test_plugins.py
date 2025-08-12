import importlib
import json
import logging
import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import plugins as plugins_module
from dungeoncrawler.items import Item, Weapon


def test_discover_plugins_skips_faulty(monkeypatch, tmp_path, caplog):
    # create temporary mods package
    (tmp_path / "__init__.py").write_text("")
    (tmp_path / "good.py").write_text("")
    (tmp_path / "bad.py").write_text("raise ImportError('boom')")

    mod_pkg = types.ModuleType("mods")
    mod_pkg.__path__ = [str(tmp_path)]
    monkeypatch.setitem(sys.modules, "mods", mod_pkg)
    monkeypatch.setattr(plugins_module, "MODS_DIR", tmp_path)

    caplog.set_level(logging.WARNING)
    modules = plugins_module.discover_plugins()

    assert any(m.__name__ == "mods.good" for m in modules)
    assert all(m.__name__ != "mods.bad" for m in modules)
    assert "bad" in caplog.text


def _create_mod(monkeypatch, tmp_path, data_files):
    """Set up a temporary mods package with one plugin and given data files."""
    plugin_dir = tmp_path / "tempmod"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    data_dir = plugin_dir / "data"
    data_dir.mkdir()
    for filename, content in data_files.items():
        (data_dir / filename).write_text(json.dumps(content))

    mod_pkg = types.ModuleType("mods")
    mod_pkg.__path__ = [str(tmp_path)]
    monkeypatch.setitem(sys.modules, "mods", mod_pkg)
    monkeypatch.setattr(plugins_module, "MODS_DIR", tmp_path)
    importlib.invalidate_caches()
    return "tempmod"


def test_apply_enemy_plugins(monkeypatch, tmp_path):
    enemy_json = {"Test Orc": {"stats": [1, 2, 3, 4], "ability": "smash"}}
    mod_name = _create_mod(monkeypatch, tmp_path, {"enemies.json": enemy_json})

    enemy_stats, enemy_abilities = {}, {}
    try:
        plugins_module.apply_enemy_plugins(enemy_stats, enemy_abilities)
    finally:
        sys.modules.pop(f"mods.{mod_name}", None)

    assert enemy_stats["Test Orc"] == (1, 2, 3, 4)
    assert enemy_abilities["Test Orc"] == "smash"


def test_apply_item_plugins(monkeypatch, tmp_path):
    items_json = {
        "weapons": [
            {
                "name": "Test Sword",
                "description": "A sword",
                "min_damage": 1,
                "max_damage": 2,
                "price": 5,
            }
        ],
        "items": [{"name": "Test Potion", "description": "A potion"}],
    }
    mod_name = _create_mod(monkeypatch, tmp_path, {"items.json": items_json})

    shop_items = []
    try:
        plugins_module.apply_item_plugins(shop_items)
    finally:
        sys.modules.pop(f"mods.{mod_name}", None)

    names = [i.name for i in shop_items]
    assert "Test Sword" in names
    assert "Test Potion" in names
    assert any(isinstance(i, Weapon) for i in shop_items if i.name == "Test Sword")
    assert any(isinstance(i, Item) for i in shop_items if i.name == "Test Potion")
