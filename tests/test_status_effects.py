import pytest

from dungeoncrawler.status_effects import (
    STATUS_EFFECT_HANDLERS,
    apply_status_effects,
)


class Player:
    """Simple entity used for status effect tests."""

    def __init__(self, health=10, attack_power=5, status_effects=None):
        self.health = health
        self.attack_power = attack_power
        self.status_effects = status_effects or {}
        self.name = "hero"


@pytest.mark.parametrize(
    "effect,damage",
    [
        ("poison", 3),
        ("burn", 4),
        ("bleed", 2),
    ],
)
def test_damage_effects(effect, damage):
    player = Player(status_effects={effect: 1})
    apply_status_effects(player)
    assert player.health == 10 - damage
    assert effect not in player.status_effects


@pytest.mark.parametrize("effect", ["freeze", "stun"])
def test_skip_turn_effects(effect):
    player = Player(status_effects={effect: 1})
    assert apply_status_effects(player) is True
    assert effect not in player.status_effects


def test_shield_expires():
    player = Player(status_effects={"shield": 1})
    assert apply_status_effects(player) is False
    assert "shield" not in player.status_effects


def test_inspire_temporarily_boosts_attack():
    player = Player(attack_power=5, status_effects={"inspire": 3})
    apply_status_effects(player)
    assert player.attack_power == 8
    apply_status_effects(player)
    apply_status_effects(player)
    assert player.attack_power == 5
    assert "inspire" not in player.status_effects


def test_custom_effect_via_registry(monkeypatch):
    def handler(entity, effects, is_player, name):
        entity.health += 5
        del effects["heal"]
        return False

    monkeypatch.setitem(STATUS_EFFECT_HANDLERS, "heal", handler)
    player = Player(health=5, status_effects={"heal": 1})
    apply_status_effects(player)
    assert player.health == 10
    assert "heal" not in player.status_effects


def test_blessed_and_cursed_expire():
    player = Player(status_effects={"blessed": 2, "cursed": 2})
    apply_status_effects(player)
    assert player.status_effects["blessed"] == 1
    assert player.status_effects["cursed"] == 1
    apply_status_effects(player)
    assert "blessed" not in player.status_effects
    assert "cursed" not in player.status_effects
