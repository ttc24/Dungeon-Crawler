import os
import sys
import random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from dungeoncrawler.entities import Player, Enemy, Weapon


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


def test_player_damage_in_range(player):
    random.seed(1)
    dmg = player.calculate_damage()
    assert player.weapon.min_damage <= dmg <= player.weapon.max_damage


def test_enemy_damage_in_range(player):
    random.seed(1)
    enemy = Enemy("Orc", 30, 20, 0, 0)
    start = player.health
    enemy.attack(player)
    dealt = start - player.health
    assert 10 <= dealt <= 20
