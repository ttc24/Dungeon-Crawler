import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player, create_guild_champion
from dungeoncrawler.events import TrialEvent
from dungeoncrawler.hooks.guild_trials import Hooks


def test_join_guild_adds_skill():
    player = Player("Hero")
    player.join_guild("Warriors' Guild")
    assert player.guild == "Warriors' Guild"
    assert any(s["name"] == "Warrior Technique" for s in player.skills.values())


def test_trials_objective_met_after_two_events():
    game = DungeonBase(5, 5)
    game.player = Player("Hero")
    hook = Hooks()
    state = game._make_state(1)
    assert not hook.on_objective_check(state, None)
    TrialEvent("Strength").trigger(game)
    state = game._make_state(1)
    assert not hook.on_objective_check(state, None)
    TrialEvent("Wisdom").trigger(game)
    state = game._make_state(1)
    assert hook.on_objective_check(state, None)


def test_guild_champion_mirrors_player():
    player = Player("Hero")
    player.choose_class("Mage")
    champ = create_guild_champion(player)
    assert champ.name == "Guild Champion"
    assert champ.health == player.max_health
    assert champ.attack_power == player.attack_power
