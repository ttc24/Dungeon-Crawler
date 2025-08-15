import random

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Companion, Enemy, Player


def test_attack_companion_deals_damage(monkeypatch):
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    enemy = Enemy("Goblin", 5, 0, 0, 0)
    wolf = Companion("Wolf", attack_power=5)
    game.player.companions.append(wolf)

    monkeypatch.setattr("builtins.input", lambda _: "2")  # defend

    def rigged_randint(a, b):
        if (a, b) == (1, 100):
            return a
        return b

    monkeypatch.setattr(random, "randint", rigged_randint)

    game.battle(enemy)

    assert enemy.health == 0


def test_healer_companion_restores_health(monkeypatch):
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    game.player.health = 50
    enemy = Enemy("Goblin", 1, 0, 0, 0)
    healer = Companion("Cleric", heal_amount=10)
    game.player.companions.append(healer)

    monkeypatch.setattr("builtins.input", lambda _: "1")  # attack

    def rigged_randint(a, b):
        if (a, b) == (1, 100):
            return a
        return b

    monkeypatch.setattr(random, "randint", rigged_randint)

    game.battle(enemy)

    assert game.player.health == 60
