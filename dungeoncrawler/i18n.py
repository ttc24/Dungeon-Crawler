import gettext
import locale
from pathlib import Path


def set_language(lang: str | None = None) -> None:
    """Initialize translations for the given language code.

    Parameters
    ----------
    lang:
        Optional two-letter language code.  If omitted the system locale is
        used.  Falls back to the built-in untranslated strings when the
        requested language is not available.
    """
    if lang is None:
        try:
            locale.setlocale(locale.LC_ALL, "")
        except locale.Error:
            lang = None
        else:
            lang = locale.getlocale()[0]

    if lang:
        lang = lang.split("_")[0]

    localedir = Path(__file__).resolve().parent.parent / "locale"
    languages = [lang] if lang else None
    gettext.translation("messages", localedir=localedir, languages=languages, fallback=True).install()
