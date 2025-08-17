"""Tests for graceful degradation of :func:`load_items`."""

import dungeoncrawler.data as data_module


def test_load_items_missing_file(monkeypatch, tmp_path):
    """``load_items`` should return empty lists if ``items.json`` is absent."""

    monkeypatch.setattr(data_module, "DATA_DIR", tmp_path)
    data_module.load_items.cache_clear()
    try:
        assert data_module.load_items() == ([], [])
    finally:
        data_module.load_items.cache_clear()


def test_load_items_invalid_json(monkeypatch, tmp_path):
    """``load_items`` should return empty lists if ``items.json`` is malformed."""

    items_path = tmp_path / "items.json"
    items_path.write_text("not valid json", encoding="utf-8")
    monkeypatch.setattr(data_module, "DATA_DIR", tmp_path)
    data_module.load_items.cache_clear()
    try:
        assert data_module.load_items() == ([], [])
    finally:
        data_module.load_items.cache_clear()
