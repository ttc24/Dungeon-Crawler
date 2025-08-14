import gettext
import locale

from dungeoncrawler import i18n


def test_set_language_handles_missing_locale(monkeypatch):
    """``set_language`` should fall back gracefully when locale can't be determined."""

    # Simulate failing locale configuration
    def fake_setlocale(*_args, **_kwargs):
        raise locale.Error

    monkeypatch.setattr(locale, "setlocale", fake_setlocale)

    captured = {}

    def fake_translation(domain, localedir=None, languages=None, fallback=False):  # noqa: D401
        captured["languages"] = languages

        class Dummy:
            def install(self):
                return None

        return Dummy()

    monkeypatch.setattr(gettext, "translation", fake_translation)

    # Should not raise and should call translation with languages=None
    i18n.set_language()
    assert captured["languages"] is None
