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


def test_heal_multiplier_applies_to_potion():
    player = Entity("Hero", {"health": 10, "max_health": 30, "heal_multiplier": 0.5})
    player.inventory.append("potion")
    enemy = Entity("Gob", {"health": 10})
    events = resolve_player_action(player, enemy, "use_health_potion")
    assert player.stats["health"] == 20
    assert events[0].value == 10


def test_enemy_defend_grants_riposte_bonus(monkeypatch):
    player = Entity("Hero", {"health": 20, "attack": 8})
    enemy = Entity("Guard", {"health": 20, "attack": 5, "speed": 5})
    enemy.intent = iter([("defend", ""), ("attack", "")])
    resolve_enemy_turn(enemy, player)
    assert "defend_attack" in enemy.status
    assert "defend_damage" in enemy.status
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: 1)
    resolve_attack(player, enemy)
    assert "defend_damage" not in enemy.status
    assert "defend_attack" in enemy.status
    rolls = iter([80, 1])
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls))
    events = resolve_enemy_turn(enemy, player)
    assert events[1].damage > 0
    assert "defend_attack" not in enemy.status
