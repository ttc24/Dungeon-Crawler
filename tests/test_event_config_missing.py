from dungeoncrawler import events


def test_load_event_config_missing_file(monkeypatch, tmp_path):
    # Point DATA_DIR to an empty directory to simulate a missing events.json
    monkeypatch.setattr(events, "DATA_DIR", tmp_path)
    events.load_event_config.cache_clear()
    assert events.load_event_config() == {}
