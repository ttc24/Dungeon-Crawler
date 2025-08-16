from pathlib import Path

from dungeoncrawler.config import Config, load_config


def test_load_config_handles_oserror(monkeypatch, tmp_path):
    """``load_config`` should gracefully handle file read errors.

    If reading the configuration file raises ``OSError`` the function should
    fall back to default settings instead of propagating the exception.
    """

    cfg_file = tmp_path / "config.json"
    cfg_file.write_text("{}")

    def bad_read_text(self, *args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(Path, "read_text", bad_read_text)

    assert load_config(cfg_file) == Config()
