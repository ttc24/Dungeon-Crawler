import json

import pytest

from dungeoncrawler.config import load_config


def test_load_config_valid(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"screen_width": 20, "screen_height": 15, "max_floors": 5}))
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


@pytest.mark.parametrize("key", ["screen_width", "screen_height", "max_floors"])
def test_load_config_negative_values(tmp_path, key):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({key: -1}))
    with pytest.raises(ValueError):
        load_config(cfg_file)


def test_new_keys_default(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text("{}")
    cfg = load_config(cfg_file)
    assert cfg.trap_chance == 0.1
    assert cfg.loot_multiplier == 1.0
    assert cfg.verbose_combat is False
    assert cfg.enable_debug is False


def test_unknown_keys_preserved(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"future_option": 42}))
    cfg = load_config(cfg_file)
    assert cfg.extras["future_option"] == 42
