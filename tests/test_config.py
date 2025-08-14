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


# The README notes that numeric settings must be positive integers. These tests
# mirror those examples to provide clearer coverage of invalid configuration
# values.


def test_readme_negative_screen_width(tmp_path):
    """Loading a config with a negative ``screen_width`` raises ``ValueError``."""

    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"screen_width": -5}))
    with pytest.raises(ValueError):
        load_config(cfg_file)


def test_readme_negative_max_floors(tmp_path):
    """Loading a config with a negative ``max_floors`` raises ``ValueError``."""

    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"max_floors": -3}))
    with pytest.raises(ValueError):
        load_config(cfg_file)


def test_new_keys_default(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text("{}")
    cfg = load_config(cfg_file)
    assert cfg.trap_chance == 0.1
    assert cfg.loot_mult == 1.0
    assert cfg.enemy_hp_mult == 1.0
    assert cfg.enemy_dmg_mult == 1.0
    assert cfg.verbose_combat is False
    assert cfg.slow_messages is False
    assert cfg.key_repeat_delay == 0.5
    assert cfg.colorblind_mode is False
    assert cfg.enable_debug is False


def test_unknown_keys_preserved(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"future_option": 42}))
    cfg = load_config(cfg_file)
    assert cfg.extras["future_option"] == 42


def test_key_repeat_delay_validation(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"key_repeat_delay": -1}))
    with pytest.raises(ValueError):
        load_config(cfg_file)
    cfg_file.write_text(json.dumps({"key_repeat_delay": "fast"}))
    with pytest.raises(ValueError):
        load_config(cfg_file)


def test_bool_toggle_validation(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"slow_messages": "yes"}))
    with pytest.raises(ValueError):
        load_config(cfg_file)
    cfg_file.write_text(json.dumps({"colorblind_mode": "no"}))
    with pytest.raises(ValueError):
        load_config(cfg_file)


def test_multiplier_validation(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"enemy_hp_mult": 0}))
    with pytest.raises(ValueError):
        load_config(cfg_file)
    cfg_file.write_text(json.dumps({"enemy_dmg_mult": -1}))
    with pytest.raises(ValueError):
        load_config(cfg_file)
    cfg_file.write_text(json.dumps({"loot_mult": 0}))
    with pytest.raises(ValueError):
        load_config(cfg_file)
