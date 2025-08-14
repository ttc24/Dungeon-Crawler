import random

from dungeoncrawler.entities import Enemy, Player


def test_novice_luck_hit_bonus(monkeypatch):
    player = Player("Hero")
    enemy = Enemy("Rat", 5, 1, 0, 0)
    player.novice_luck_active = True

    monkeypatch.setattr(random, "randint", lambda a, b: 90)
    monkeypatch.setattr(player, "calculate_damage", lambda: 1)
    player.attack(enemy)
    assert enemy.health == 4

    enemy.health = enemy.max_health
    player.novice_luck_active = False
    player.attack(enemy)
    assert enemy.health == enemy.max_health


def test_novice_luck_damage_reduction():
    player = Player("Hero")
    start = player.health
    player.novice_luck_active = True
    player.take_damage(5)
    assert player.health == start - 4

    player.health = start
    player.novice_luck_active = False
    player.take_damage(5)
    assert player.health == start - 5
