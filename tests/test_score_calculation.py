from dungeoncrawler.entities import Player


def test_score_style_bonuses():
    player = Player("Tester")
    player.level = 2
    player.gold = 120
    player.inventory.extend([object(), object()])
    player.health = player.max_health

    breakdown = player.get_score_breakdown()
    assert breakdown["level"] == 200
    assert breakdown["inventory"] == 20
    assert breakdown["gold"] == 120
    assert breakdown["style"]["no_damage"] == 50
    assert breakdown["style"]["rich"] == 50
    assert breakdown["total"] == 440
