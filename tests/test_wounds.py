import dungeoncrawler.entities as entities
from dungeoncrawler.config import Config
from dungeoncrawler.entities import Player


def test_wounds_reduce_and_cleanse():
    p = Player("Hero")
    base = p.max_health
    p.add_wound(2)
    assert p.max_health == base - 10
    p.cleanse_wounds()
    assert p.max_health == base


def test_wound_soft_cap_and_decay(monkeypatch):
    cfg = Config(
        wounds_soft_cap_last_n_floors=1,
        wounds_soft_cap_ratio=0.30,
        wounds_decay_per_floor=0.5,
    )
    monkeypatch.setattr(entities, "config", cfg)
    p = Player("Hero")
    base = p.max_health
    p.apply_wound(10)
    assert p.wounds == 6
    assert p.max_health == base - 30
    p.decay_wounds()
    assert p.wounds == 3
    assert p.max_health == base - 15
    p.apply_wound(10)
    assert p.wounds == 9
    assert p.max_health == base - 45
