from types import SimpleNamespace

from types import SimpleNamespace

from dungeoncrawler.entities import Player, Enemy
from dungeoncrawler.hooks import floor17
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.status_effects import apply_status_effects
from dungeoncrawler.events import ShrineEvent


def make_state(player, enemies=None, config=None):
    enemies = enemies or []
    game = SimpleNamespace(last_action=None, last_cost=0)
    state = SimpleNamespace(player=player, enemies=enemies, game=game, config=config or SimpleNamespace(loot_mult=1.0))
    return state


def test_fester_mark_overheal():
    player = Player("Hero")
    state = make_state(player)
    hook = floor17.Hooks()
    hook.on_floor_start(state, None)
    player.health = player.max_health - 1
    healed = player.heal(10)
    assert healed == 1
    assert "fester_mark" in player.status_effects
    apply_status_effects(player)
    assert player.health == player.max_health - player._fester_mark_damage


def test_soul_tax_stack_and_expire():
    player = Player("Hero")
    enemy = Enemy("Goblin", 10, 2, 0, 0)
    base_attack = player.attack_power
    config = SimpleNamespace(loot_mult=1.0)
    state = make_state(player, [enemy], config)
    hook = floor17.Hooks()
    hook.on_floor_start(state, None)
    state.enemies = []
    hook.on_turn(state, None)
    assert player.attack_power == base_attack - 1
    assert config.loot_mult > 1.0
    for _ in range(10):
        apply_status_effects(player)
    assert player.attack_power == base_attack
    assert config.loot_mult == 1.0


def test_altar_donation_clears_soul_tax():
    player = Player("Hero")
    enemy = Enemy("Goblin", 10, 2, 0, 0)
    config = SimpleNamespace(loot_mult=1.0)
    state = make_state(player, [enemy], config)
    hook = floor17.Hooks()
    hook.on_floor_start(state, None)
    base_attack = player.attack_power
    state.enemies = []
    hook.on_turn(state, None)
    player.credits = 100
    event = ShrineEvent()
    game = SimpleNamespace(player=player, stats_logger=SimpleNamespace(record_reward=lambda: None), config=config)
    event.trigger(game, input_func=lambda *_: "d", output_func=lambda *a, **k: None)
    assert player.attack_power == base_attack and not player._soul_tax_timers
    assert config.loot_mult == player._soul_tax_base_loot
    assert player.credits == 50


def test_floor17_config_has_miniboss_sequence():
    dungeon = DungeonBase(5, 5)
    cfg = dungeon.floor_configs[17]
    assert cfg["boss_slots"] == 3
    assert cfg["boss_pool"].count("Gloom Shade") == 1
