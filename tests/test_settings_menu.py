from dungeoncrawler.config import Config, load_config, settings_menu


def test_settings_menu_updates_and_saves(tmp_path):
    cfg = Config()
    cfg_file = tmp_path / "config.json"

    inputs = iter(["12", "8", "0.2", "1.5", "1.2", "1.3", "y"])
    outputs = []

    def fake_input(_prompt: str) -> str:
        return next(inputs)

    def fake_output(msg: str) -> None:
        outputs.append(msg)

    new_cfg = settings_menu(cfg, path=cfg_file, input_func=fake_input, output_func=fake_output)
    assert new_cfg.screen_width == 12
    assert new_cfg.screen_height == 8
    assert new_cfg.trap_chance == 0.2
    assert new_cfg.enemy_hp_mult == 1.5
    assert new_cfg.enemy_dmg_mult == 1.2
    assert new_cfg.loot_mult == 1.3
    assert new_cfg.colorblind_mode is True

    loaded = load_config(cfg_file)
    assert loaded.screen_width == 12
    assert loaded.colorblind_mode is True
