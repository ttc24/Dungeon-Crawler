import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from dungeoncrawler.ai import AggressiveAI, DefensiveAI
from dungeoncrawler.entities import Enemy, Player, Weapon


@pytest.fixture
def player():
    p = Player("Hero")
    p.weapon = Weapon("Test Sword", "", 10, 10, 0)
    return p


@pytest.fixture
def enemy():
    e = Enemy("Goblin", 20, 5, 0, 10)
    e.xp = 5
    return e


def test_player_attack_defeats_enemy(player, enemy):
    enemy.health = 5
    random.seed(0)
    player.attack(enemy)
    assert enemy.health == 0
    assert player.xp == 5
    assert player.gold == 10


def test_enemy_attack_applies_status(player):
    enemy = Enemy("Wraith", 10, 10, 0, 0, ability="poison")
    random.seed(0)
    initial_health = player.health
    enemy.attack(player)
    assert player.health < initial_health
    assert player.status_effects["poison"] == 3


def test_status_effects_tick():
    p = Player("Hero")
    p.health = 50
    p.status_effects["poison"] = 2
    p.apply_status_effects()
    assert p.health == 47
    assert p.status_effects["poison"] == 1


def test_bleed_effect():
    p = Player("Hero")
    p.health = 30
    p.status_effects["bleed"] = 2
    p.apply_status_effects()
    assert p.health == 28
    assert p.status_effects["bleed"] == 1


def test_stun_effect_skips_enemy_turn():
    e = Enemy("Orc", 20, 5, 0, 5)
    e.status_effects["stun"] = 1
    skip = e.apply_status_effects()
    assert skip is True
    assert "stun" not in e.status_effects


def test_shield_reduces_damage():
    e = Enemy("Orc", 20, 10, 0, 0)
    e.status_effects["shield"] = 1
    e.take_damage(10)
    assert e.health == 15


def test_aggressive_ai_attacks(player):
    enemy = Enemy("Goblin", 20, 6, 0, 0, ai=AggressiveAI())
    initial = player.health
    random.seed(0)
    enemy.take_turn(player)
    assert player.health < initial


def test_defensive_ai_defends(player):
    enemy = Enemy("Goblin", 20, 6, 0, 0, ai=DefensiveAI())
    enemy.health = 5
    enemy.take_turn(player)
    assert "shield" in enemy.status_effects


def test_player_damage_range():
    player = Player("Hero")
    player.weapon = Weapon("Variance Blade", "", 10, 20, 0)
    enemy = Enemy("Training Dummy", 100, 0, 0, 0)
    random.seed(0)
    start = enemy.health
    player.attack(enemy)
    damage = start - enemy.health
    assert 10 <= damage <= 20


def test_enemy_damage_range(player):
    enemy = Enemy("Orc", 30, 20, 0, 0)
    random.seed(0)
    start = player.health
    enemy.attack(player)
    damage = start - player.health
    assert 10 <= damage <= 20


def test_player_flee_success():
    player = Player("Hero")
    enemy = Enemy("Goblin", 10, 0, 0, 0, speed=5)
    player.speed = 20
    random.seed(0)
    assert player.flee(enemy) is True
    assert "advantage" not in enemy.status_effects


def test_player_flee_failure_gives_enemy_advantage():
    player = Player("Hero")
    enemy = Enemy("Goblin", 10, 5, 0, 0, speed=10)
    player.speed = 10
    random.seed(0)
    assert player.flee(enemy) is False
    assert enemy.status_effects.get("advantage") == 1
    random.seed(30)
    before = player.health
    enemy.attack(player)
    assert player.health < before
    assert "advantage" not in enemy.status_effects
