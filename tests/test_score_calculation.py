from dungeoncrawler.entities import Player


def test_score_style_bonuses():
    player = Player("Tester")
    player.level = 2
    player.credits = 120
    player.inventory.extend([object(), object()])
    player.health = player.max_health

    breakdown = player.get_score_breakdown()
    assert breakdown["level"] == 200
    assert breakdown["inventory"] == 20
    assert breakdown["credits"] == 120
    assert breakdown["style"]["no_damage"] == 50
    assert breakdown["style"]["rich"] == 50
    assert breakdown["total"] == 440


def test_format_score_breakdown_lines():
    player = Player("Tester")
    player.level = 1
    player.inventory.append(object())
    player.credits = 5
    player.health = player.max_health

    lines = player.format_score_breakdown()
    assert lines == [
        "Score Breakdown:",
        "  Level: 100",
        "  Inventory: 10",
        "  Credits: 5",
        "  No Damage: 50",
    ]
