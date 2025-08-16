from types import SimpleNamespace

from dungeoncrawler.entities import Player
from dungeoncrawler.hooks import floor14
from dungeoncrawler.status_effects import add_status_effect, apply_status_effects


def make_state(player):
    state = SimpleNamespace(player=player, log=[], game=SimpleNamespace(last_action=None))
    state.queue_message = state.log.append
    return state


def test_debt_stacks_and_consumption(monkeypatch):
    player = Player("Hero")
    state = make_state(player)
    hook = floor14.Hooks()
    monkeypatch.setattr("dungeoncrawler.hooks.floor14.random.random", lambda: 0.9)
    for _ in range(12):
        state.game.last_action = "move"
        hook.on_turn(state, None)
    assert player.status_effects["entropic_debt"] == 10
    state.game.last_action = "wait"
    hook.on_turn(state, None)
    assert player.status_effects["entropic_debt"] == 8
    state.game.last_action = "defend"
    hook.on_turn(state, None)
    assert player.status_effects["entropic_debt"] == 6
    health = player.health
    apply_status_effects(player)
    assert player.health == health - 6


def test_cold_tick_damage():
    player = Player("Hero")
    state = make_state(player)
    hook = floor14.Hooks()
    state.game.last_action = "wait"
    start = player.health
    hook.on_turn(state, None)
    assert player.health == start - 1


def test_slippery_movement(monkeypatch):
    player = Player("Hero")
    state = make_state(player)
    hook = floor14.Hooks()
    state.game.last_action = "move"
    monkeypatch.setattr("dungeoncrawler.hooks.floor14.random.random", lambda: 0.05)
    hook.on_turn(state, None)
    assert any("slip" in msg for msg in state.log)
    assert "entropic_debt" not in player.status_effects


def test_totem_clears_and_spawns_add(monkeypatch):
    player = Player("Hero")
    player.status_effects["entropic_debt"] = 5
    state = make_state(player)
    hook = floor14.Hooks()
    monkeypatch.setattr("dungeoncrawler.hooks.floor14.random.random", lambda: 0.1)
    spawned = hook.vent_to_totem(state)
    assert spawned is True
    assert "entropic_debt" not in player.status_effects


def test_spiteful_reflection(monkeypatch):
    attacker = Player("Atk")
    defender = Player("Def")
    defender.status_effects["spiteful_reflection"] = 1
    monkeypatch.setattr("dungeoncrawler.status_effects.random.random", lambda: 0.1)
    add_status_effect(defender, "poison", 3, source=attacker)
    assert "poison" in attacker.status_effects
    attacker2 = Player("Atk2")
    defender2 = Player("Def2")
    defender2.status_effects["spiteful_reflection"] = 1
    monkeypatch.setattr("dungeoncrawler.status_effects.random.random", lambda: 0.9)
    add_status_effect(defender2, "poison", 3, source=attacker2)
    assert "poison" not in attacker2.status_effects
