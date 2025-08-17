from __future__ import annotations

"""OS-specific paths for game data and configuration."""

import shutil
from pathlib import Path

from platformdirs import user_config_path, user_data_path

APP_NAME = "dungeon_crawler"

# Base directories determined by platformdirs
SAVE_DIR = Path(user_data_path(APP_NAME)) / "saves"
CONFIG_DIR = Path(user_config_path(APP_NAME))
# Legacy directory used by older versions of the game
LEGACY_DIR = Path.home() / ".dungeon_crawler"


def ensure_dirs() -> None:
    """Ensure necessary directories exist."""
    for path in (SAVE_DIR, CONFIG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def migrate_legacy() -> None:
    """Migrate data from the old ``~/.dungeon_crawler`` location."""
    if not LEGACY_DIR.exists():
        return
    ensure_dirs()
    target_base = SAVE_DIR.parent
    try:
        # Move saves directory
        legacy_saves = LEGACY_DIR / "saves"
        if legacy_saves.exists():
            for item in legacy_saves.iterdir():
                dest = SAVE_DIR / item.name
                if not dest.exists():
                    shutil.move(str(item), dest)
        # Move top-level files such as scores and run stats
        for name in ("scores.json", "run_stats.json"):
            src = LEGACY_DIR / name
            dest = target_base / name
            if src.exists() and not dest.exists():
                shutil.move(str(src), dest)
        # Attempt to clean up empty legacy directories
        try:
            legacy_saves.rmdir()
        except OSError:
            pass
        try:
            LEGACY_DIR.rmdir()
        except OSError:
            pass
    except Exception:
        # Migration failures should not prevent the game from starting
        pass
