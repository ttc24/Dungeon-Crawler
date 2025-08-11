import os
import sys
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from dungeoncrawler.entities import Player, Enemy, Weapon
from dungeoncrawler.ai import AggressiveAI, DefensiveAI


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
    p.status_effects['poison'] = 2
    p.apply_status_effects()
    assert p.health == 47
    assert p.status_effects['poison'] == 1


def test_bleed_effect():
    p = Player("Hero")
    p.health = 30
    p.status_effects['bleed'] = 2
    p.apply_status_effects()
    assert p.health == 28
    assert p.status_effects['bleed'] == 1


def test_stun_effect_skips_enemy_turn():
    e = Enemy("Orc", 20, 5, 0, 5)
    e.status_effects['stun'] = 1
    skip = e.apply_status_effects()
    assert skip is True
    assert 'stun' not in e.status_effects


def test_shield_reduces_damage():
    e = Enemy("Orc", 20, 10, 0, 0)
    e.status_effects['shield'] = 1
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
    assert 'shield' in enemy.status_effects
