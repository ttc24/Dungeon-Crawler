import random

from dungeoncrawler.entities import Enemy
from dungeoncrawler.items import Weapon


def test_calculate_damage_seeded(player):
    player.attack_power = 10
    random.seed(1)
    assert player.calculate_damage() == 6


def test_attack_applies_status_effect(player):
    enemy = Enemy("goblin", 20, 5, 0, 0)
    player.weapon = Weapon("Poisoned Blade", "", 5, 10, effect="poison")
    random.seed(0)
    player.attack(enemy)
    assert enemy.health == 12
    assert enemy.status_effects.get("poison") == 3
