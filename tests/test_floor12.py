from types import SimpleNamespace

from dungeoncrawler.entities import Player
from dungeoncrawler.items import Item
from dungeoncrawler.status_effects import apply_status_effects

from dungeoncrawler.hooks import floor12


def test_blood_torrent_stacks_and_vision_bonus():
    player = Player("Hero")
    state = SimpleNamespace(player=player, enemy_vision_bonus=0)
    hook = floor12.Hooks()
    hook.apply_blood_torrent(state)
    hook.apply_blood_torrent(state)
    hook.apply_blood_torrent(state)
    hook.apply_blood_torrent(state)  # cap at 3
    assert player.status_effects["blood_torrent"] == 3
    health = player.health
    apply_status_effects(player)
    assert player.health == health - 3
    player.heal(5)
    assert "blood_torrent" in player.status_effects
    hook.on_turn(state, None)
    assert state.enemy_vision_bonus == 3


def test_compression_sickness_penalty_and_wait():
    player = Player("Hero")
    state = SimpleNamespace(player=player)
    hook = floor12.Hooks()
    hook.trigger_compression_sickness(state)
    apply_status_effects(player)
    assert player.speed == 9
    assert player.status_effects["compression_sickness"] == 4
    player.wait()
    assert player.status_effects["compression_sickness"] == 2


def test_items_clear_effects():
    player = Player("Hero")
    player.status_effects["blood_torrent"] = 2
    player.inventory.append(Item("Scent-mask Spray", ""))
    player.use_item("Scent-mask Spray")
    assert "blood_torrent" not in player.status_effects
    player.status_effects["blood_torrent"] = 1
    player.inventory.append(Item("Absorbent Gel", ""))
    player.use_item("Absorbent Gel")
    assert "blood_torrent" not in player.status_effects
    hook = floor12.Hooks()
    state = SimpleNamespace(player=player)
    hook.trigger_compression_sickness(state)
    apply_status_effects(player)
    player.inventory.append(Item("Anti-Nausea Draught", ""))
    player.use_item("Anti-Nausea Draught")
    assert "compression_sickness" not in player.status_effects
    assert player.speed == 10
