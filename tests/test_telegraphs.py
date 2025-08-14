import json

from dungeoncrawler.ai import IntentAI


class DummyEnemy:
    def __init__(self, name):
        self.name = name
        self.health = 10
        self.max_health = 10
        self.status_effects = {}
        self.heavy_cd = 0


def test_floor_enemies_have_custom_telegraphs():
    with open("data/floors.json") as f:
        floors = json.load(f)
    enemies = set()
    for cfg in floors.values():
        enemies.update(cfg["enemies"])

    ai = IntentAI(aggressive=1, defensive=0, unpredictable=0)
    for name in enemies:
        dummy = DummyEnemy(name)
        _action, msg = ai.choose_intent(dummy, dummy)
        default = f"The {name} winds up for a heavy strike…"
        assert msg and msg != default


def test_bosses_have_custom_telegraphs():
    from dungeoncrawler.dungeon import BOSS_STATS

    ai = IntentAI(aggressive=1, defensive=0, unpredictable=0)
    for name in BOSS_STATS:
        dummy = DummyEnemy(name)
        _action, msg = ai.choose_intent(dummy, dummy)
        default = f"The {name} winds up for a heavy strike…"
        assert msg and msg != default
