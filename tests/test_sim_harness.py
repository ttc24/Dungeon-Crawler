from dungeoncrawler.sim import simulate_battles


def test_simulate_battles():
    stats = simulate_battles("Bandit", runs=5, seed=0)
    assert 0 <= stats["winrate"] <= 1
    assert stats["avg_turns"] >= 0
