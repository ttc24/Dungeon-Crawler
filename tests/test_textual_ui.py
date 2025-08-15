import pytest

from dungeoncrawler.ui import DungeonApp

textual = pytest.importorskip("textual")
App = textual.app.App


def test_dungeon_app_instantiation() -> None:
    """DungeonApp can be constructed when textual is available."""
    app = DungeonApp()
    assert isinstance(app, App)
