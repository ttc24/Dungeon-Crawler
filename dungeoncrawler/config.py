from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


@dataclass
class Config:
    """Game configuration loaded from ``config.json``.

    Defaults mirror the previous hard-coded constants so the game remains
    playable even if no configuration file is provided.
    """

    save_file: str = "savegame.json"
    score_file: str = "scores.json"
    max_floors: int = 18
    screen_width: int = 10
    screen_height: int = 10


def load_config(path: Path = CONFIG_PATH) -> Config:
    """Load configuration from ``path`` if it exists.

    Parameters
    ----------
    path:
        Location of the JSON configuration file.  Defaults to
        ``config.json`` in the project root.

    Returns
    -------
    Config
        A :class:`Config` instance populated with values from the JSON file or
        falling back to defaults when the file or specific keys are missing.
    """

    cfg = Config()
    if path.exists():
        try:
            data: dict[str, Any] = json.loads(path.read_text())
        except json.JSONDecodeError:
            return cfg
        for key, value in data.items():
            if hasattr(cfg, key):
                setattr(cfg, key, value)
    return cfg


# Load configuration at import so other modules can simply import ``config``.
config = load_config()
