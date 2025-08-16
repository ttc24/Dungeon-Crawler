from dungeoncrawler.scoring import compute_score_breakdown


def test_early_retire_bonus_applies_before_floor_9():
    state = {"base": 1000, "floor": 5, "died": False}
    breakdown = compute_score_breakdown(state)
    # 4 floors before retire floor at 8% each -> 32% of base
    assert breakdown["retire_bonus"] == 320
    # No death bonus applies
    assert breakdown["no_death_bonus"] == 100
    assert breakdown["death_penalty"] == 0
    assert breakdown["total"] == 1420
