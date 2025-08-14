from dungeoncrawler.core.combat import (
    calculate_hit,
    resolve_attack,
    resolve_enemy_turn,
    resolve_player_action,
)
from dungeoncrawler.core.entity import Entity


def test_defend_reduces_damage_and_boosts_hit(monkeypatch):
    rolls = iter([1, 100])
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls))
    player = Entity("Hero", {"health": 10, "attack": 5, "speed": 5})
    enemy = Entity("Gob", {"health": 10, "attack": 10, "speed": 5})
    resolve_player_action(player, enemy, "defend")
    assert "defend_damage" in player.status
    assert "defend_attack" in player.status
    resolve_enemy_turn(enemy, player)
    assert player.stats["health"] == 4
    assert "defend_damage" not in player.status
    hit = calculate_hit(player, enemy)
    assert hit == 85
    assert "defend_attack" not in player.status


def test_flee_action_speed_difference(monkeypatch):
    rolls = iter([1, 100, 1, 100])
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls))
    fast = Entity("Hero", {"health": 10, "speed": 15})
    slow_enemy = Entity("Gob", {"health": 10, "speed": 5})
    events = resolve_player_action(fast, slow_enemy, "flee")
    assert events[0].value == 1
    assert "advantage" not in slow_enemy.status

    slow = Entity("Hero", {"health": 10, "speed": 10})
    fast_enemy = Entity("Gob", {"health": 10, "speed": 10})
    events = resolve_player_action(slow, fast_enemy, "flee")
    assert events[0].value == 0
    assert "advantage" in fast_enemy.status
    resolve_enemy_turn(fast_enemy, slow)
    assert "advantage" not in fast_enemy.status


def test_critical_hits_double_damage(monkeypatch):
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: 1)
    attacker = Entity("A", {"health": 10, "attack": 5, "crit": 150})
    defender = Entity("D", {"health": 20, "defense": 1})
    event = resolve_attack(attacker, defender)
    assert event.damage == 8
    assert defender.stats["health"] == 12
