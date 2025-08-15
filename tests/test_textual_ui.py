import pytest

pytest.importorskip("textual")

from textual.app import App

from dungeoncrawler.ui import DungeonApp


def test_dungeon_app_instantiation() -> None:
    """DungeonApp can be constructed when textual is available."""
    app = DungeonApp()
    assert isinstance(app, App)
