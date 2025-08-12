import builtins

from dungeoncrawler import constants
from dungeoncrawler import dungeon as dungeon_module
from dungeoncrawler.entities import Player


def test_riddles_loaded_and_used(monkeypatch, capsys):
    # Ensure riddles were loaded from the data file and contain many entries
    assert isinstance(constants.RIDDLES, list)
    assert len(constants.RIDDLES) >= 5

    chosen = constants.RIDDLES[-1]
    # Restrict the riddles list in the dungeon module so the trap
    # must use our chosen riddle
    monkeypatch.setattr(dungeon_module, "RIDDLES", [chosen])
    monkeypatch.setattr(builtins, "input", lambda _: chosen["answer"])

    dungeon = dungeon_module.DungeonBase(2, 1)
    dungeon.player = Player("Hero")
    # Position the player and a trap in the dungeon
    dungeon.rooms[0][0] = "Trap"
    dungeon.rooms[0][1] = dungeon.player
    dungeon.player.x = 1
    dungeon.player.y = 0

    dungeon.handle_room(0, 0)
    out = capsys.readouterr().out
    assert chosen["question"] in out
