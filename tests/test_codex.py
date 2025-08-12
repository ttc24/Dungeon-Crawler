import random
from dungeoncrawler.events import LoreNoteEvent
from dungeoncrawler.entities import Player, Enemy
from dungeoncrawler.dungeon import DungeonBase


def test_lore_note_event_buff(monkeypatch):
    player = Player("Hero")
    class Game:
        pass
    game = Game()
    game.player = player
    event = LoreNoteEvent()
    def fake_choice(seq):
        return seq[-1]
    monkeypatch.setattr(random, "choice", fake_choice)
    event.trigger(game, output_func=lambda _ : None)
    assert player.codex
    assert "beetle_bane" in player.status_effects
    assert player.status_effects["beetle_bane"] == 10


def test_codex_command(capsys):
    game = DungeonBase(5, 5)
    game.player = Player("Hero")
    game.player.codex = ["Note A", "Note B"]
    assert game.handle_input(":codex")
    out = capsys.readouterr().out
    assert "Note A" in out and "Note B" in out


def test_codex_persistence(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr("dungeoncrawler.dungeon.SAVE_FILE", save_path)
    monkeypatch.setattr("dungeoncrawler.constants.SAVE_FILE", save_path)
    game = DungeonBase(5, 5)
    game.player = Player("Hero")
    game.player.codex.append("Ancient note")
    game.save_game(1)
    new_game = DungeonBase(5, 5)
    floor = new_game.load_game()
    assert new_game.player.codex == ["Ancient note"]
    assert floor == 1


def test_beetle_bane_attack_bonus(monkeypatch):
    player = Player("Hero")
    enemy = Enemy("Giant Beetle", 5, 1, 0, 0)
    player.status_effects["beetle_bane"] = 1
    player.calculate_damage = lambda: 1
    monkeypatch.setattr(random, "randint", lambda a, b: 86)
    player.attack(enemy)
    assert enemy.health == 4

