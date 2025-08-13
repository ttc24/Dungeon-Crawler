from dungeoncrawler.core.combat import (
    resolve_attack,
    resolve_enemy_turn,
    resolve_player_action,
)
from dungeoncrawler.core.entity import Entity
from dungeoncrawler.core.events import AttackResolved, StatusApplied
from dungeoncrawler.core.map import GameMap


def test_attack_returns_event():
    attacker = Entity("A", {"health": 10, "attack": 5})
    defender = Entity("D", {"health": 8, "defense": 1})
    event = resolve_attack(attacker, defender)
    assert isinstance(event, AttackResolved)
    assert event.damage == 4
    assert event.defeated == 0


def test_player_action_defend_event():
    player = Entity("Hero", {"health": 10})
    enemy = Entity("Gob", {"health": 5})
    events = resolve_player_action(player, enemy, "defend")
    assert isinstance(events[0], StatusApplied)
    assert events[0].status == "defending"


def test_use_potion_event():
    player = Entity("Hero", {"health": 5, "potion_heal": 5, "max_health": 10})
    player.inventory = ["potion"]
    enemy = Entity("Gob", {"health": 5})
    events = resolve_player_action(player, enemy, "use_health_potion")
    assert isinstance(events[0], StatusApplied)
    assert events[0].status == "healed"
    assert events[0].value == 5


def test_enemy_turn_returns_attack_event():
    player = Entity("Hero", {"health": 10})
    enemy = Entity("Gob", {"health": 5, "attack": 3})
    events = resolve_enemy_turn(enemy, player)
    assert isinstance(events[0], AttackResolved)


def test_update_visibility_yields_events():
    grid = [[1, 1], [1, 1]]
    gm = GameMap(grid)
    events = gm.update_visibility(0, 0, 1)
    coords = {(e.x, e.y) for e in events}
    assert coords == {(0, 0), (1, 0), (0, 1)}
    # calling again should yield no new events
    assert gm.update_visibility(0, 0, 1) == []
