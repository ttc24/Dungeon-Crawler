from dungeoncrawler import map as map_module


def test_move_player_blocks_out_of_bounds(game):
    game.player.x = 0
    game.player.y = 0
    game.rooms[0][0] = game.player
    msg = map_module.move_player(game, "left")
    assert msg == "You can't move that way."
    assert (game.player.x, game.player.y) == (0, 0)


def test_move_player_updates_visibility(game):
    game.player.x = 1
    game.player.y = 1
    game.rooms[1][1] = game.player
    game.rooms[1][2] = []
    game.visible = [[False for _ in range(game.width)] for _ in range(game.height)]
    game.discovered = [[False for _ in range(game.width)] for _ in range(game.height)]
    map_module.move_player(game, "right")
    assert (game.player.x, game.player.y) == (2, 1)
    assert game.visible[1][2]
    assert game.discovered[1][2]
