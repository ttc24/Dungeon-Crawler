import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import map as dungeon_map
from dungeoncrawler.dungeon import (
    BOSS_LOOT,
    BOSS_TRAITS,
    DungeonBase,
)
from dungeoncrawler.data import load_floor_definitions
from dungeoncrawler.entities import Enemy, Player


def test_boss_drops_loot(monkeypatch):
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    boss_name = next(iter(BOSS_LOOT))
    enemy = Enemy(boss_name, 1, 0, 0, 0)

    monkeypatch.setattr("builtins.input", lambda _: "1")
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    game.battle(enemy)

    assert BOSS_LOOT[boss_name][0] in game.player.inventory


def test_stat_boost_when_no_loot(monkeypatch):
    load_floor_definitions()
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    monkeypatch.setitem(game.boss_loot, "Bone Tyrant", [])
    base = game.player.attack_power
    dungeon_map.generate_dungeon(game, floor=1)
    assert game.player.attack_power == base + 1


def test_boss_regenerates_trait():
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    name = "Glacier Fiend"
    hp, atk, dfs, gold, ability = game.boss_stats[name]
    enemy = Enemy(name, hp, atk, dfs, gold, ability, traits=BOSS_TRAITS[name])
    enemy.health -= 10
    before = enemy.health
    enemy.apply_status_effects()
    assert enemy.health > before
