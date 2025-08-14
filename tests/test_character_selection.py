import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


def _setup():
    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("hero")
    return dungeon


def test_offer_class_permanent_and_skills(capsys):
    dungeon = _setup()
    inputs = iter(["1"])
    dungeon.offer_class(input_func=lambda _: next(inputs))
    out = capsys.readouterr().out.lower()
    assert "permanent" in out
    assert "power strike" in out
    assert dungeon.player.class_type != "Novice"


def test_offer_guild_screen(capsys):
    dungeon = _setup()
    dungeon.offer_guild(input_func=lambda _: "1")
    out = capsys.readouterr().out.lower()
    assert "permanent" in out
    assert "power strike" in out
    assert dungeon.player.guild == "Warriors' Guild"


def test_offer_race_screen(capsys):
    dungeon = _setup()
    dungeon.offer_race(input_func=lambda _: "2")
    out = capsys.readouterr().out.lower()
    assert "permanent" in out
    assert "power strike" in out
    assert dungeon.player.race == "Elf"
