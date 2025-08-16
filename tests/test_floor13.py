from types import SimpleNamespace

from dungeoncrawler.entities import Enemy, Player
from dungeoncrawler.hooks import floor13
from dungeoncrawler.items import Item, Trinket


def test_spell_cost_increased():
    player = Player("Hero")
    enemy = Enemy("Gob", 10, 1, 0, 0)
    state = SimpleNamespace(player=player)
    hook = floor13.Hooks()
    hook.on_floor_start(state, None)
    stamina = player.stamina
    player.use_skill(enemy, "1")
    base = player.skills["1"]["cost"]
    assert player.stamina == stamina - int(base * 1.5)


def test_cleanse_failure(monkeypatch):
    player = Player("Hero")
    player.status_effects["mana_lock"] = 1
    player.status_effects["blood_torrent"] = 1
    player.inventory.append(Item("Scent-mask Spray", ""))
    monkeypatch.setattr("dungeoncrawler.status_effects.random.random", lambda: 0.1)
    player.use_item("Scent-mask Spray")
    assert "blood_torrent" in player.status_effects
    player.inventory.append(Item("Scent-mask Spray", ""))
    monkeypatch.setattr("dungeoncrawler.status_effects.random.random", lambda: 0.9)
    player.use_item("Scent-mask Spray")
    assert "blood_torrent" not in player.status_effects


def test_shield_reduction():
    player = Player("Hero")
    player.status_effects["dull_wards"] = 1
    player.status_effects["shield"] = 1
    health = player.health
    player.take_damage(10)
    assert player.health == health - (10 - int(5 * 0.7))


def test_crit_cannot_bypass_shield():
    player = Player("Hero")
    player.status_effects["shield"] = 1
    health = player.health
    player.take_damage(10, critical=True)
    assert player.health == health - 10
    player = Player("Hero")
    player.status_effects["shield"] = 1
    player.status_effects["dull_wards"] = 1
    health = player.health
    player.take_damage(10, critical=True)
    assert player.health == health - (10 - int(5 * 0.7))


def test_suppression_ring_overheat(monkeypatch):
    player = Player("Hero")
    ring = Trinket("Suppression Ring", "")
    player.inventory.append(ring)
    player.equip_trinket(ring)
    player.status_effects["mana_lock"] = 1
    enemy = Enemy("Gob", 10, 1, 0, 0)
    monkeypatch.setattr("dungeoncrawler.status_effects.random.random", lambda: 0.0)
    stamina = player.stamina
    player.use_skill(enemy, "1")
    base = player.skills["1"]["cost"]
    assert player.stamina == stamina - base
    assert player.trinket is None
