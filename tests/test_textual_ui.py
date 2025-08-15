import pytest

pytest.importorskip("textual")

from dungeoncrawler.ui import DungeonApp
from textual.app import App


def test_dungeon_app_instantiation() -> None:
    """DungeonApp can be constructed when textual is available."""
    app = DungeonApp()
    assert isinstance(app, App)
