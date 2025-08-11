from dungeoncrawler.entities import Enemy, Player
from dungeoncrawler.main import build_character


def test_build_character(monkeypatch):
    inputs = iter(
        [
            "",
            "Alice",  # name (invalid then valid)
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    player = build_character()
    assert isinstance(player, Player)
    assert player.name == "Alice"
    assert player.class_type == "Novice"
    assert player.race is None
    assert player.guild is None


def test_choose_barbarian_stats():
    player = Player("Bob")
    player.choose_class("Barbarian")
    assert player.class_type == "Barbarian"
    assert player.max_health == 130
    assert player.attack_power == 12


def test_warlock_skill_lifesteal(monkeypatch):
    player = Player("Hexer")
    player.choose_class("Warlock")
    enemy = Enemy("Dummy", 100, 5, 0, 0)
    player.health = 70

    monkeypatch.setattr("random.randint", lambda a, b: 10)
    player.use_skill(enemy)
    expected_damage = player.attack_power + 10
    assert enemy.health == 100 - expected_damage
    assert player.health == 70 + min(expected_damage // 2, player.max_health - 70)
    assert player.skill_cooldown == 3


def test_race_and_guild_bonuses():
    player = Player("Eve")
    player.choose_race("Tiefling")
    assert player.attack_power == 12
    player.join_guild("Healers' Circle")
    assert player.max_health == 108
    assert player.health == 108
