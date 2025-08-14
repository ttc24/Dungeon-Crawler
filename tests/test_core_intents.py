from dungeoncrawler.core.combat import resolve_attack, resolve_enemy_turn
from dungeoncrawler.core.entity import Entity, make_enemy
from dungeoncrawler.core.events import AttackResolved, IntentTelegraphed, StatusApplied


def test_telegraph_precedes_action(monkeypatch):
    rolls = iter([1, 100])
    monkeypatch.setattr(
        "dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls)
    )
    player = Entity("Hero", {"health": 10})
    enemy = make_enemy("Goblin Skirm")
    events = resolve_enemy_turn(enemy, player)
    assert isinstance(events[0], IntentTelegraphed)
    assert isinstance(events[1], AttackResolved)


def test_defend_consumption(monkeypatch):
    rolls = iter([1, 100, 1, 100])
    monkeypatch.setattr(
        "dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls)
    )
    player = Entity("Hero", {"health": 20, "attack": 8})
    enemy = make_enemy("Guard Beetle")
    events = resolve_enemy_turn(enemy, player)
    assert isinstance(events[0], IntentTelegraphed)
    assert isinstance(events[1], StatusApplied)
    assert "defend_damage" in enemy.status
    assert "defend_attack" in enemy.status

    # Player attacks, consuming defend_damage
    resolve_attack(player, enemy)
    assert "defend_damage" not in enemy.status
    assert "defend_attack" in enemy.status

    # Beetle attacks next turn, consuming defend_attack
    events2 = resolve_enemy_turn(enemy, player)
    assert isinstance(events2[0], IntentTelegraphed)
    assert isinstance(events2[1], AttackResolved)
    assert "defend_attack" not in enemy.status
