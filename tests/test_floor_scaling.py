from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler import map as dungeon_map
from dungeoncrawler.entities import Player
from dungeoncrawler.config import config


def test_floor10_scaling_applies(monkeypatch):
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Tester")
    monkeypatch.setattr(dungeon_map, "generate_dungeon", lambda *a, **k: None)
    original_hp, original_dmg = config.enemy_hp_mult, config.enemy_dmg_mult
    config.enable_debug = False
    dungeon.generate_dungeon(10)
    assert config.enemy_hp_mult == original_hp + 0.15
    assert config.enemy_dmg_mult == original_dmg + 0.10
    config.enemy_hp_mult = original_hp
    config.enemy_dmg_mult = original_dmg


def test_floor10_scaling_disabled_in_debug(monkeypatch):
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Tester")
    monkeypatch.setattr(dungeon_map, "generate_dungeon", lambda *a, **k: None)
    original_hp, original_dmg = config.enemy_hp_mult, config.enemy_dmg_mult
    config.enable_debug = True
    dungeon.generate_dungeon(10)
    assert config.enemy_hp_mult == original_hp
    assert config.enemy_dmg_mult == original_dmg
    config.enable_debug = False
