from dungeoncrawler.core.combat import calculate_hit, resolve_attack, resolve_enemy_turn
from dungeoncrawler.core.entity import Entity, make_enemy
from dungeoncrawler.core.events import AttackResolved, IntentTelegraphed, StatusApplied


def test_telegraph_precedes_action(monkeypatch):
    rolls = iter([1, 100])
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls))
    player = Entity("Hero", {"health": 10})
    enemy = make_enemy("Goblin Skirm")
    events = resolve_enemy_turn(enemy, player)
    assert isinstance(events[0], IntentTelegraphed)
    assert isinstance(events[1], AttackResolved)


def test_defend_consumption(monkeypatch):
    rolls = iter([1, 100, 1, 100])
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls))
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


def test_heavy_attack_increases_damage(monkeypatch):
    rolls = iter([1, 100])
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls))
    player = Entity("Hero", {"health": 50})
    enemy = Entity("Orc", {"health": 10, "attack": 10})
    enemy.intent = (item for item in [("heavy_attack", "")])
    events = resolve_enemy_turn(enemy, player)
    assert isinstance(events[1], AttackResolved)
    assert events[1].damage == 15
    assert player.stats["health"] == 35


def test_wild_attack_accuracy_penalty(monkeypatch):
    rolls = iter([60])
    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: next(rolls))
    player = Entity("Hero", {"health": 50})
    enemy = Entity("Orc", {"health": 10, "attack": 10})
    base_hit = calculate_hit(enemy, player)
    assert base_hit == 75
    enemy.intent = (item for item in [("wild_attack", "")])
    events = resolve_enemy_turn(enemy, player)
    assert isinstance(events[1], AttackResolved)
    assert events[1].damage == 0
    assert player.stats["health"] == 50
