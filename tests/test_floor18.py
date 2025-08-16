from types import SimpleNamespace

from dungeoncrawler.entities import Enemy, Player
from dungeoncrawler.hooks import floor18
from dungeoncrawler.status_effects import add_status_effect, apply_status_effects


def make_state(player, enemies=None):
    enemies = enemies or []
    game = SimpleNamespace(last_action=None)
    state = SimpleNamespace(player=player, enemies=enemies, game=game, log=[])
    state.queue_message = state.log.append
    return state


def test_spotlight_ping_and_counters():
    player = Player("Hero")
    enemy = Enemy("Goblin", 10, 10, 0, 0)
    enemy.rarity = "elite"
    state = make_state(player, [enemy])
    hook = floor18.Hooks()
    hook.on_floor_start(state, None)
    add_status_effect(player, "spotlight_ping", 1)
    player.x, player.y = 2, 3
    base = enemy.attack_power
    hook.on_turn(state, None)
    assert state.spotlight_ping == (2, 3)
    assert enemy.attack_power == int(base * 1.1)
    hook.use_jammer(state)
    hook.on_turn(state, None)
    assert state.spotlight_ping is None
    assert enemy.attack_power == base
    add_status_effect(player, "spotlight_ping", 1)
    hook.on_turn(state, None)
    assert enemy.attack_power == int(base * 1.1)
    hook.use_stealth(state)
    hook.on_turn(state, None)
    assert state.spotlight_ping is None
    assert enemy.attack_power == base


def test_audience_fatigue_stacks_and_rewrite():
    player = Player("Hero")
    state = make_state(player)
    hook = floor18.Hooks()
    hook.on_floor_start(state, None)
    for _ in range(6):
        state.game.last_action = "Fireball"
        hook.on_turn(state, None)
    assert player.status_effects["audience_fatigue"] == 4
    assert getattr(player, "_audience_fatigue_timers", []) == [3, 3, 3, 3]
    apply_status_effects(player)
    assert player.status_effects["audience_fatigue"] == 4
    hook.use_rewrite(state)
    assert "audience_fatigue" not in player.status_effects
    assert getattr(player, "_audience_fatigue_timers", []) == []
