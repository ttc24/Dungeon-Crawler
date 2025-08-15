from dungeoncrawler import map as map_module
from dungeoncrawler.config import config
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Enemy, Player


def _find_enemy(game):
    for row in game.rooms:
        for obj in row:
            if isinstance(obj, Enemy):
                return obj


def test_enemy_stats_scaled_by_config(monkeypatch):
    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("Hero")
    dungeon.floor_configs[1].update({"enemy_pool": ["Goblin"], "boss_pool": [], "size": (5, 5)})
    monkeypatch.setattr(map_module.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(map_module.random, "randint", lambda a, b: a)
    base_hp, base_dmg = config.enemy_hp_mult, config.enemy_dmg_mult
    config.enemy_hp_mult = 2.0
    config.enemy_dmg_mult = 3.0
    try:
        map_module.generate_dungeon(dungeon, 1)
        enemy = _find_enemy(dungeon)
        assert enemy.health == 102
        assert enemy.attack_power == 24
    finally:
        config.enemy_hp_mult = base_hp
        config.enemy_dmg_mult = base_dmg


def test_loot_multiplier_scales_treasure(monkeypatch):
    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("Hero")
    dungeon.floor_configs[1].update({"enemy_pool": [], "boss_pool": [], "size": (5, 5)})
    dungeon.default_place_counts = {"Treasure": 1}
    monkeypatch.setattr(map_module.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(map_module.random, "randint", lambda a, b: a)
    base_loot = config.loot_mult
    config.loot_mult = 2.0
    try:
        map_module.generate_dungeon(dungeon, 1)
        treasure_count = sum(row.count("Treasure") for row in dungeon.rooms)
        assert treasure_count == 2
    finally:
        config.loot_mult = base_loot

