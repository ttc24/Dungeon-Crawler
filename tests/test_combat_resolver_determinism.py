import random
from dungeoncrawler.core.combat import resolve_player_action, resolve_enemy_turn
from dungeoncrawler.core.entity import Entity


def test_combat_resolver_deterministic_with_seed():
    player1 = Entity("Hero", {"health": 10, "attack": 4})
    enemy1 = Entity("Goblin", {"health": 6, "attack": 3})
    random.seed(123)
    events1 = []
    events1.extend(resolve_player_action(player1, enemy1, "attack"))
    events1.extend(resolve_enemy_turn(enemy1, player1))

    player2 = Entity("Hero", {"health": 10, "attack": 4})
    enemy2 = Entity("Goblin", {"health": 6, "attack": 3})
    random.seed(123)
    events2 = []
    events2.extend(resolve_player_action(player2, enemy2, "attack"))
    events2.extend(resolve_enemy_turn(enemy2, player2))

    assert events1 == events2
