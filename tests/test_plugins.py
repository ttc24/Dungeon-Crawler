import logging
import os
import sys
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import plugins as plugins_module


def test_discover_plugins_skips_faulty(monkeypatch, tmp_path, caplog):
    # create temporary mods package
    (tmp_path / "__init__.py").write_text("")
    (tmp_path / "good.py").write_text("")
    (tmp_path / "bad.py").write_text("raise ImportError('boom')")

    mod_pkg = types.ModuleType("mods")
    mod_pkg.__path__ = [str(tmp_path)]
    monkeypatch.setitem(sys.modules, "mods", mod_pkg)
    monkeypatch.setattr(plugins_module, "MODS_DIR", tmp_path)

    caplog.set_level(logging.WARNING)
    modules = plugins_module.discover_plugins()

    assert any(m.__name__ == "mods.good" for m in modules)
    assert all(m.__name__ != "mods.bad" for m in modules)
    assert "bad" in caplog.text
