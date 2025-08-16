import random

import pytest

from dungeoncrawler.ai import IntentAI
from dungeoncrawler.entities import Enemy


class DummyPlayer:
    def __init__(self):
        self.status_effects = {}


def test_intent_field_and_delayed_resolution():
    random.seed(0)
    player = DummyPlayer()
    ai = IntentAI(aggressive=0, defensive=1, unpredictable=0)
    enemy = Enemy("Goblin", 9, 5, 0, 0, ai=ai)
    enemy.health = 3  # ensure defensive intent triggers defend
    action, intent, msg = enemy.ai.choose_intent(enemy, player)
    enemy.next_action, enemy.intent, enemy.intent_message = action, intent, msg
    assert enemy.intent == "Defensive"
    assert action == "defend"
    enemy.take_turn(player)
    assert "shield" in enemy.status_effects
    assert enemy.intent is None


def test_intent_ai_requires_positive_weight():
    with pytest.raises(ValueError):
        IntentAI(0, 0, 0)
