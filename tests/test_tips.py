from dungeoncrawler.tutorial import TipsManager


def test_tips_auto_disable_after_floor_two():
    tm = TipsManager()
    assert tm.enabled is True
    # Access tips for early floors which should still be enabled
    tm.for_floor(1)
    tm.for_floor(2)
    # Accessing floor 3 should auto disable future tips
    tm.for_floor(3)
    assert tm.enabled is False
    assert tm.for_floor(4) == []
