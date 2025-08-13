from dungeoncrawler import map as map_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.items import Item


def make_game():
    game = DungeonBase(3, 3)
    game.player = Player("Hero")
    game.rooms[1][1] = game.player
    game.player.x = 1
    game.player.y = 1
    game.current_floor = 1
    return game


def test_move_player_invalid_message():
    game = make_game()
    game.messages.clear()
    map_module.move_player(game, "left")
    assert game.messages[-1] == "You can't move that way."


def test_handle_room_item_message():
    game = make_game()
    game.messages.clear()
    game.audience_gift = lambda: None
    game.check_quest_progress = lambda: None
    item = Item("Gem", "Sparkling")
    game.rooms[1][2] = item
    game.room_names[1][2] = "Plain"
    map_module.handle_room(game, 2, 1)
    assert any("You found a Gem!" in m for m in game.messages)
