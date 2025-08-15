import pytest

from dungeoncrawler.data import load_floor_definitions
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player


@pytest.fixture
def player() -> Player:
    p = Player("hero")
    p.x = 1
    p.y = 1
    return p


@pytest.fixture
def game(player: Player) -> DungeonBase:
    load_floor_definitions()
    game = DungeonBase(3, 3)
    game.current_floor = 1
    game.player = player
    # initialize simple empty grid so movement works
    game.rooms = [[[] for _ in range(game.width)] for _ in range(game.height)]
    game.room_names = [[None for _ in range(game.width)] for _ in range(game.height)]
    game.discovered = [[False for _ in range(game.width)] for _ in range(game.height)]
    game.visible = [[False for _ in range(game.width)] for _ in range(game.height)]
    game.rooms[player.y][player.x] = player
    return game
