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


def test_warrior_skill_damages():
    player = Player("war", "Warrior")
    enemy = DummyEnemy()
    hp = enemy.health
    player.use_skill(enemy)
    assert enemy.health < hp


def test_mage_skill_burns():
    player = Player("mage", "Mage")
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert "burn" in enemy.status_effects


def test_rogue_skill_damages():
    player = Player("rogue", "Rogue")
    enemy = DummyEnemy()
    hp = enemy.health
    player.use_skill(enemy)
    assert enemy.health < hp


def test_barbarian_skill_heals_and_damages():
    player = Player("barb", "Barbarian")
    player.health -= 10
    base = player.health
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert enemy.health < enemy.max_health
    assert player.health > base


def test_druid_skill_freeze_and_heal():
    player = Player("dru", "Druid")
    player.health -= 5
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert "freeze" in enemy.status_effects
    assert player.health > player.max_health - 5


def test_ranger_skill_poison():
    player = Player("rang", "Ranger")
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert "poison" in enemy.status_effects


def test_sorcerer_skill_burns():
    player = Player("sorc", "Sorcerer")
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert "burn" in enemy.status_effects


def test_monk_skill_hits_twice():
    player = Player("monk", "Monk")
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert enemy.health <= enemy.max_health - (player.attack_power + 4) * 2


def test_warlock_skill_life_drain():
    player = Player("wlock", "Warlock")
    player.health -= 10
    base = player.health
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert enemy.health < enemy.max_health
    assert player.health > base


def test_necromancer_skill_siphon():
    player = Player("necro", "Necromancer")
    player.health -= 10
    base = player.health
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert enemy.health < enemy.max_health
    assert player.health > base


def test_shaman_skill_heal_and_damage():
    player = Player("sham", "Shaman")
    player.health -= 10
    base = player.health
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert enemy.health < enemy.max_health
    assert player.health > base


def test_alchemist_skill_burns():
    player = Player("alch", "Alchemist")
    enemy = DummyEnemy()
    player.use_skill(enemy)
    assert "burn" in enemy.status_effects
