from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player, Enemy, Companion, Item
from dungeoncrawler.hooks import floor15
from dungeoncrawler.status_effects import add_status_effect, apply_status_effects


def test_brood_bloom_spawns_and_reapplies():
    host = Enemy("Host", 30, 5, 0, 0)
    spawned = []
    hook = floor15.Hooks()
    hook.infect(host, 2, lambda e: spawned.append(e.name))
    apply_status_effects(host)
    assert host.status_effects["brood_bloom"] == 1
    apply_status_effects(host)
    assert len(spawned) == 1
    assert host.status_effects["brood_bloom"] == 1
    apply_status_effects(host)
    assert len(spawned) == 2
    assert "brood_bloom" not in host.status_effects


def test_miasma_aura_and_mitigation():
    game = DungeonBase(1, 1)
    player = Player("Tester")
    companion = Companion("Ally")
    player.companions.append(companion)
    game.player = player
    game.rooms = [["Miasma Carrier"]]
    hook = floor15.Hooks()
    state = game._make_state(15)

    player.health = player.max_health - 10
    hook.on_turn(state, None)
    apply_status_effects(player)
    apply_status_effects(companion)
    assert player.heal_multiplier == 0.5
    healed = player.heal(10)
    assert healed == 5
    assert companion.heal_multiplier == 0.5

    # clear remaining aura
    apply_status_effects(player)
    apply_status_effects(companion)

    player.heal_multiplier = 1.0
    companion.heal_multiplier = 1.0
    player.status_effects.clear()
    companion.status_effects.clear()
    player.inventory.append(Item("Filter Mask", ""))
    hook.on_turn(state, None)
    apply_status_effects(player)
    apply_status_effects(companion)
    assert player.heal_multiplier == 1.0
    assert companion.heal_multiplier == 0.5
    assert not any(i.name == "Filter Mask" for i in player.inventory)

    # clear aura again
    apply_status_effects(player)
    apply_status_effects(companion)

    player.trinket = Item("Suppression Ring", "")
    player.status_effects.clear()
    companion.status_effects.clear()
    player.heal_multiplier = 1.0
    companion.heal_multiplier = 1.0
    hook.on_turn(state, None)
    apply_status_effects(player)
    apply_status_effects(companion)
    assert player.heal_multiplier == 1.0
    assert companion.heal_multiplier == 0.5


def test_broodling_fire_vulnerability():
    broodling = Enemy("Broodling", 20, 5, 0, 0, traits=["fire_vulnerable"])
    add_status_effect(broodling, "burn", 1)
    apply_status_effects(broodling)
    assert broodling.health == 12


def test_creeping_corruption_spreads_and_debuffs():
    game = DungeonBase(3, 3)
    player = Player("Hero")
    game.player = player
    hook = floor15.Hooks()
    state = game._make_state(15)
    hook.on_floor_start(state, None)
    player.status_effects["blessed"] = 1
    hook.on_turn(state, None)
    apply_status_effects(player)
    assert player.vision == 4
    assert "blessed" not in player.status_effects
    # let remaining corruption fade before moving
    apply_status_effects(player)
    apply_status_effects(player)
    player.vision = 5
    player.x = 1
    hook.on_turn(state, None)
    apply_status_effects(player)
    assert player.vision == 4
