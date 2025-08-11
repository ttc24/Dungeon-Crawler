import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler.main import build_character
from dungeoncrawler.entities import Player


def test_build_character(monkeypatch):
    inputs = iter([
        "", "Alice",          # name (invalid then valid)
        "9", "2",              # class (invalid then Mage)
        "0", "3",              # race (invalid then Dwarf)
        "5", "1"               # guild (invalid then Warriors' Guild)
    ])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    player = build_character()
    assert isinstance(player, Player)
    assert player.name == "Alice"
    assert player.class_type == "Mage"
    assert player.race == "Dwarf"
    assert player.guild == "Warriors' Guild"
