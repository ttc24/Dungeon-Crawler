from dungeoncrawler.config import config


def test_god_spawn(monkeypatch, game):
    monkeypatch.setattr(config, "enable_debug", True)
    messages = []
    monkeypatch.setattr(game.renderer, "show_message", messages.append)
    game.handle_input(":god spawn DebugSword")
    assert any(item.name == "DebugSword" for item in game.player.inventory)
    assert any("Spawned DebugSword" in m for m in messages)


def test_god_teleport(monkeypatch, game):
    monkeypatch.setattr(config, "enable_debug", True)
    messages = []
    monkeypatch.setattr(game.renderer, "show_message", messages.append)
    called = {}

    def fake_gen(floor):
        called["floor"] = floor

    monkeypatch.setattr(game, "generate_dungeon", fake_gen)
    game.handle_input(":god teleport 5")
    assert game.current_floor == 5
    assert called["floor"] == 5
    assert any("Teleported to floor 5" in m for m in messages)


def test_god_set(monkeypatch, game):
    monkeypatch.setattr(config, "enable_debug", True)
    messages = []
    monkeypatch.setattr(game.renderer, "show_message", messages.append)
    game.player.credits = 1
    game.handle_input(":god set credits 99")
    assert game.player.credits == 99
    assert any("Set credits to 99" in m for m in messages)
