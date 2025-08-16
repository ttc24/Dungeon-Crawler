from dungeoncrawler import map as dungeon_map
from dungeoncrawler.config import config
import pytest

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.config import config
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def _setup(monkeypatch):
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Tester")
    monkeypatch.setattr(dungeon_map, "generate_dungeon", lambda *a, **k: None)
    return dungeon


def test_per_floor_scaling(monkeypatch):
    dungeon = _setup(monkeypatch)
    original_hp, original_dmg = config.enemy_hp_mult, config.enemy_dmg_mult
    dungeon.generate_dungeon(3)
    try:
        assert config.enemy_hp_mult == pytest.approx(1 + 0.05 * 2)
        assert config.enemy_dmg_mult == pytest.approx(1 + 0.04 * 2)
    finally:
        config.enemy_hp_mult = original_hp
        config.enemy_dmg_mult = original_dmg


def test_hard_band_boost(monkeypatch):
    dungeon = _setup(monkeypatch)
    original_hp, original_dmg = config.enemy_hp_mult, config.enemy_dmg_mult
    dungeon.generate_dungeon(10)
    first_hp, first_dmg = config.enemy_hp_mult, config.enemy_dmg_mult
    dungeon.generate_dungeon(11)
    try:
        assert first_hp == pytest.approx(1 + 0.05 * 9 + 0.15)
        assert first_dmg == pytest.approx(1 + 0.04 * 9 + 0.10)
        assert config.enemy_hp_mult == pytest.approx(1 + 0.05 * 10 + 0.15)
        assert config.enemy_dmg_mult == pytest.approx(1 + 0.04 * 10 + 0.10)
    finally:
        config.enemy_hp_mult = original_hp
        config.enemy_dmg_mult = original_dmg


def test_scaling_disabled_in_debug(monkeypatch):
    dungeon = _setup(monkeypatch)
    original_hp, original_dmg = config.enemy_hp_mult, config.enemy_dmg_mult
    config.enable_debug = True
    dungeon.generate_dungeon(10)
    try:
        assert config.enemy_hp_mult == original_hp
        assert config.enemy_dmg_mult == original_dmg
    finally:
        config.enable_debug = False
        config.enemy_hp_mult = original_hp
        config.enemy_dmg_mult = original_dmg
