from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.items import Item
from dungeoncrawler.map import update_visibility
from dungeoncrawler.data import load_floor_definitions
from dungeoncrawler.config import config


def _open_game(floor: int) -> DungeonBase:
    load_floor_definitions()
    game = DungeonBase(20, 20)
    game.player = Player("Tester")
    game.current_floor = floor
    game.width = game.height = 20
    game.rooms = [["Empty" for _ in range(20)] for _ in range(20)]
    game.discovered = [[False for _ in range(20)] for _ in range(20)]
    game.visible = [[False for _ in range(20)] for _ in range(20)]
    game.player.x = game.player.y = 10
    return game


def test_floor_10_halves_healing(monkeypatch):
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    monkeypatch.setattr(DungeonBase, "save_game", lambda self, floor: None)
    game.generate_dungeon(10)
    game.player.health = game.player.max_health - 20
    game.player.inventory.append(Item("Health Potion", ""))
    game.player.use_health_potion()
    assert game.player.health == game.player.max_health - 10


def test_floor_11_trap_chance_increases(monkeypatch):
    base = config.trap_chance
    game = DungeonBase(1, 1)
    game.player = Player("Hero")
    monkeypatch.setattr(DungeonBase, "save_game", lambda self, floor: None)
    game.generate_dungeon(11)
    try:
        assert config.trap_chance > base
    finally:
        config.trap_chance = base


def test_floor_10_visibility_reduced():
    game = _open_game(10)
    update_visibility(game)
    px, py = game.player.x, game.player.y
    max_dist = max(
        abs(x - px) + abs(y - py)
        for y in range(game.height)
        for x in range(game.width)
        if game.visible[y][x]
    )
    assert max_dist == 4


def test_floor_12_darkness_limits_visibility():
    game = _open_game(12)
    update_visibility(game)
    px, py = game.player.x, game.player.y
    max_dist = max(
        abs(x - px) + abs(y - py)
        for y in range(game.height)
        for x in range(game.width)
        if game.visible[y][x]
    )
    assert max_dist == 3
