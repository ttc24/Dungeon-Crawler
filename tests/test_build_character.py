import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from dungeoncrawler.entities import Player
from dungeoncrawler.main import build_character


def test_build_character(tmp_path, monkeypatch):
    run_file = tmp_path / "run.json"
    monkeypatch.setattr("dungeoncrawler.constants.RUN_FILE", run_file)
    monkeypatch.setattr("dungeoncrawler.main.RUN_FILE", run_file)
    inputs = iter(
        [
            "",
            "Alice",  # name (invalid then valid)
        ]
    )

    player = build_character(input_func=lambda _: next(inputs), output_func=lambda _msg: None)
    assert isinstance(player, Player)
    assert player.name == "Alice"
    assert player.class_type == "Novice"
    assert player.race is None
    assert player.guild is None


def test_choose_barbarian_stats():
    player = Player("Bob")
    player.choose_class("Barbarian")
    assert player.class_type == "Barbarian"
    assert player.max_health == 130
    assert player.attack_power == 12


@pytest.mark.parametrize(
    "cls,hp,atk",
    [
        ("Druid", 100, 11),
        ("Sorcerer", 75, 15),
        ("Monk", 95, 13),
        ("Warlock", 85, 14),
        ("Necromancer", 90, 13),
        ("Shaman", 110, 10),
        ("Alchemist", 90, 12),
    ],
)
def test_new_class_stats(cls, hp, atk):
    player = Player("Test")
    player.choose_class(cls)
    assert player.class_type == cls
    assert player.max_health == hp
    assert player.attack_power == atk


def test_race_and_guild_bonuses():
    player = Player("Eve")
    player.choose_race("Tiefling")
    assert player.attack_power == 12
    player.join_guild("Healers' Circle")
    assert player.max_health == 108
    assert player.health == 108


@pytest.mark.parametrize(
    "race,hp,atk",
    [
        ("Tiefling", 100, 12),
        ("Dragonborn", 102, 12),
        ("Goblin", 100, 11),
    ],
)
def test_new_race_bonuses(race, hp, atk):
    player = Player("Sam")
    player.choose_race(race)
    assert player.max_health == hp
    assert player.attack_power == atk


def test_class_abilities_and_costs():
    barb = Player("Grok")
    barb.choose_class("Barbarian")
    assert barb.class_abilities["Rage"]["cost"] == 30
    druid = Player("Leaf")
    druid.choose_class("Druid")
    assert druid.class_abilities["Wild Shape"]["cost"] == 35


def test_shadow_brotherhood_perk():
    player = Player("Shade")
    base_costs = {k: v["cost"] for k, v in player.skills.items()}
    player.join_guild("Shadow Brotherhood")
    assert player.attack_power == 14
    for key, skill in player.skills.items():
        assert skill["cost"] == max(0, base_costs[key] - 5)


def test_racial_traits_recorded():
    t = Player("Infernal")
    t.choose_race("Tiefling")
    assert "Infernal resistance" in t.racial_traits
    d = Player("Draco")
    d.choose_race("Dragonborn")
    assert "Draconic breath" in d.racial_traits
