import random

from dungeoncrawler.combat import battle
from dungeoncrawler.entities import Enemy


def test_combat_logging(game):
    random.seed(0)
    game.stats_logger.start_floor(game, 1)
    game.player.attack_power = 10
    enemy = Enemy("Dummy", 5, 0, 0, 0)
    battle(game, enemy, input_func=lambda _="": "1")
    row = game.stats_logger.combat_rows[0]
    assert row["enemy"] == "Dummy"
    assert row["turns"] >= 1
    assert row["damage_dealt"] >= 0
