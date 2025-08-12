import json

import pytest

from dungeoncrawler.config import load_config


def test_load_config_valid(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(
        json.dumps({"screen_width": 20, "screen_height": 15, "max_floors": 5})
    )
    cfg = load_config(cfg_file)
    assert cfg.screen_width == 20
    assert cfg.screen_height == 15
    assert cfg.max_floors == 5


def test_load_config_invalid_type(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"screen_width": "wide"}))
    with pytest.raises(ValueError):
        load_config(cfg_file)


def test_load_config_invalid_range(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"screen_height": 0}))
    with pytest.raises(ValueError):
        load_config(cfg_file)
