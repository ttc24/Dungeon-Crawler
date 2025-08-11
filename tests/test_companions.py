import os
import sys
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player, Enemy, Companion
from dungeoncrawler.combat import battle


def test_attack_companion_deals_damage(monkeypatch):
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    enemy = Enemy("Goblin", 5, 0, 0, 0)
    wolf = Companion("Wolf", attack_power=5)
    game.player.companions.append(wolf)

    monkeypatch.setattr('builtins.input', lambda _: '2')  # defend
    monkeypatch.setattr(random, 'randint', lambda a, b: b)

    battle(game, enemy)

    assert enemy.health == 0


def test_healer_companion_restores_health(monkeypatch):
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    game.player.health = 50
    enemy = Enemy("Goblin", 1, 0, 0, 0)
    healer = Companion("Cleric", heal_amount=10)
    game.player.companions.append(healer)

    monkeypatch.setattr('builtins.input', lambda _: '1')  # attack
    monkeypatch.setattr(random, 'randint', lambda a, b: b)

    battle(game, enemy)

    assert game.player.health == 60
