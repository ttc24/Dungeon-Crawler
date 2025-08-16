from types import SimpleNamespace

from dungeoncrawler.entities import Player, Enemy
from dungeoncrawler.hooks import floor16
from dungeoncrawler.status_effects import apply_status_effects


def make_state(player, enemies=None):
    enemies = enemies or []
    game = SimpleNamespace(last_action=None, last_cost=0, repeat_action=None, repeat_target=None)
    state = SimpleNamespace(player=player, enemies=enemies, game=game, log=[])
    state.queue_message = state.log.append
    return state


def test_temporal_lag_repeats_and_refunds(monkeypatch):
    player = Player("Hero")
    enemy = Enemy("Goblin", 10, 2, 0, 0)
    state = make_state(player, [enemy])
    hook = floor16.Hooks()
    hook.on_floor_start(state, None)
    state.game.last_action = "attack"
    state.game.last_cost = 10
    player.stamina -= 10
    monkeypatch.setattr("dungeoncrawler.status_effects.random.random", lambda: 0.1)
    hook.on_turn(state, None)
    assert state.game.repeat_action == "attack"
    assert state.game.repeat_target in {player, enemy}
    assert player.stamina == 100


def test_anchor_clears_temporal_lag(monkeypatch):
    player = Player("Hero")
    state = make_state(player)
    hook = floor16.Hooks()
    hook.on_floor_start(state, None)
    hook.use_anchor(state)
    state.game.last_action = "attack"
    state.game.last_cost = 10
    player.stamina -= 10
    monkeypatch.setattr("dungeoncrawler.status_effects.random.random", lambda: 0.1)
    hook.on_turn(state, None)
    assert state.game.repeat_action is None
    assert player.stamina == 90


def test_haste_dysphoria_inverts_speed():
    player = Player("Hero")
    state = make_state(player)
    hook = floor16.Hooks()
    hook.on_floor_start(state, None)
    apply_status_effects(player)
    player.speed = 13
    apply_status_effects(player)
    assert player.speed == 7
