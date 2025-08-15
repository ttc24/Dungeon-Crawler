import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.data import load_floor_definitions
from dungeoncrawler.entities import Player
from dungeoncrawler.events import MiniQuestHookEvent
from dungeoncrawler.quests import EscortNPC, EscortQuest


def setup_game():
    load_floor_definitions()
    game = DungeonBase(5, 5)
    game.player = Player("hero")
    return game


def test_mini_quest_hook_starts_quest():
    game = setup_game()
    event = MiniQuestHookEvent()
    outputs = []
    event.trigger(game, output_func=outputs.append)
    assert isinstance(game.active_quest, EscortQuest)
    assert any("escort" in msg.lower() for msg in outputs)


def test_mini_quest_hook_existing_quest():
    game = setup_game()
    npc = EscortNPC("Test NPC")
    quest = EscortQuest(npc, reward=10, flavor="Existing quest")
    game.active_quest = quest
    event = MiniQuestHookEvent()
    outputs = []
    event.trigger(game, output_func=outputs.append)
    assert game.active_quest is quest
    assert any("quest ongoing" in msg.lower() for msg in outputs)
