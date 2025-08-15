"""Visibility and discovery handling tests."""

from dungeoncrawler.core.map import GameMap


def test_visibility_and_discovery_on_small_map():
    """Ensure walls block vision and discovered matches visible tiles."""

    # 3x3 map with walls (None) blocking horizontal movement
    grid = [
        [1, 1, 1],
        [None, 1, None],
        [1, 1, 1],
    ]
    gm = GameMap(grid)

    gm.update_visibility(1, 1, 2)

    expected = [
        [True, True, True],
        [False, True, False],
        [True, True, True],
    ]

    assert gm.visible == expected
    assert gm.discovered == expected


def test_light_radius_limits_visibility():
    """Visibility should be restricted by the given light radius."""

    grid = [[1 for _ in range(5)] for _ in range(5)]
    gm = GameMap(grid)
    gm.update_visibility(2, 2, 1)

    expected = [
        [False, False, False, False, False],
        [False, False, True, False, False],
        [False, True, True, True, False],
        [False, False, True, False, False],
        [False, False, False, False, False],
    ]

    assert gm.visible == expected


def test_light_radius_limits_monster_detection():
    grid = [[1 for _ in range(5)] for _ in range(5)]
    gm = GameMap(grid)
    # Player at (0,0) with small light radius cannot see enemy at (4,4)
    gm.update_visibility(0, 0, 2)
    assert gm.visible[4][4] is False
    # Enemy with limited sight cannot detect player
    enemy_view = gm.compute_visibility(4, 4, 2)
    assert (0, 0) not in enemy_view
    # Increasing enemy sight reveals the player
    enemy_view_far = gm.compute_visibility(4, 4, 8)
    assert (0, 0) in enemy_view_far
