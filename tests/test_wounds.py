from dungeoncrawler.entities import Player


def test_wounds_reduce_and_cleanse():
    p = Player("Hero")
    base = p.max_health
    p.add_wound(2)
    assert p.max_health == base - 10
    p.cleanse_wounds()
    assert p.max_health == base
