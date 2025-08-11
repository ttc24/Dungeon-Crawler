import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.entities import Enemy, Player


class DummyEnemy(Enemy):
    def __init__(self):
        super().__init__("Dummy", 100, 10, 0, 0)


def test_cleric_skill_heals():
    player = Player("test", "Cleric")
    player.health = player.health - 20
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert player.health > player.max_health - 20
    assert player.skill_cooldown > 0


def test_paladin_skill_damage_and_heal():
    player = Player("pal", "Paladin")
    player.health -= 5
    enemy = DummyEnemy()
    enemy_hp = enemy.health
    player.use_skill(enemy)
    assert enemy.health < enemy_hp
    assert player.health > player.max_health - 5


def test_bard_inspire_buff():
    player = Player("bard", "Bard")
    enemy = DummyEnemy()
    base_attack = player.attack_power
    player.use_skill(enemy)
    assert "inspire" in player.status_effects
    player.apply_status_effects()
    assert player.attack_power == base_attack + 3
    player.apply_status_effects()
    player.apply_status_effects()
    assert "inspire" not in player.status_effects
    assert player.attack_power == base_attack
