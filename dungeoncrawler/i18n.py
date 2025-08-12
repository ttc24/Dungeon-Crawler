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
        lang = locale.getdefaultlocale()[0]
    if lang:
        lang = lang.split("_")[0]
    localedir = Path(__file__).resolve().parent.parent / "locale"
    gettext.translation("messages", localedir=localedir, languages=[lang], fallback=True).install()
