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
