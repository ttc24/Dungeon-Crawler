from dungeoncrawler.entities import Enemy
from dungeoncrawler.status_effects import add_status_effect


def test_elite_status_resistance():
    enemy = Enemy("Dummy", 10, 2, 0, 0)
    enemy.rarity = "elite"
    add_status_effect(enemy, "poison", 4)
    assert enemy.status_effects["poison"] == 2
