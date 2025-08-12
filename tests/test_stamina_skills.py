from dungeoncrawler.entities import Enemy, Player


def test_power_strike_consumes_stamina_and_cooldown(monkeypatch):
    player = Player("Hero")
    enemy = Enemy("Dummy", 100, 5, 0, 0)
    vals = iter([1, 10])
    monkeypatch.setattr("random.randint", lambda a, b: next(vals))
    player.use_skill(enemy, choice="1")
    assert player.stamina == 70
    assert player.skills["1"]["cooldown"] == 3
    assert enemy.health == 85


def test_insufficient_stamina_message(capsys):
    player = Player("Hero")
    enemy = Enemy("Dummy", 100, 5, 0, 0)
    player.stamina = 10
    player.use_skill(enemy, choice="1")
    out = capsys.readouterr().out
    assert "You're winded" in out
    assert enemy.health == 100
    assert player.skills["1"]["cooldown"] == 0


def test_feint_staggers_enemy(monkeypatch):
    player = Player("Hero")
    enemy = Enemy("Dummy", 100, 5, 0, 0)
    vals = iter([1, 10])
    monkeypatch.setattr("random.randint", lambda a, b: next(vals))
    player.use_skill(enemy, choice="2")
    assert enemy.health == 95
    assert enemy.status_effects["stagger"] == 1


def test_bandage_heals_and_removes_bleed():
    player = Player("Hero")
    enemy = Enemy("Dummy", 100, 5, 0, 0)
    player.health = player.max_health - 5
    player.status_effects["bleed"] = 3
    player.use_skill(enemy, choice="3")
    assert "bleed" not in player.status_effects
    assert player.health == player.max_health - 2
    assert player.stamina == 75
    assert player.skills["3"]["cooldown"] == 5


def test_wait_regenerates_stamina():
    player = Player("Hero")
    player.stamina = 50
    player.wait()
    assert player.stamina == 60

