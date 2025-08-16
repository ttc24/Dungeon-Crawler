from dungeoncrawler.entities import Enemy
from dungeoncrawler.status_effects import add_status_effect


def test_elite_status_resistance_activates_after_floor10():
    enemy = Enemy("Dummy", 10, 2, 0, 0)
    enemy.rarity = "elite"
    enemy.floor = 9
    add_status_effect(enemy, "poison", 4)
    assert enemy.status_effects["poison"] == 4
    enemy.floor = 10
    add_status_effect(enemy, "burn", 4)
    assert enemy.status_effects["burn"] == 2
