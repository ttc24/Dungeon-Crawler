from __future__ import annotations

import json
from dataclasses import dataclass
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
    verbose_combat: bool = False


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

    Raises
    ------
    ValueError
        If a configuration value has an invalid type or falls outside the
        accepted range. For example ``screen_width`` and ``screen_height`` must
        be positive integers.
    """

    cfg = Config()
    if path.exists():
        try:
            data: dict[str, Any] = json.loads(path.read_text())
        except json.JSONDecodeError:
            return cfg
        for key, value in data.items():
            if hasattr(cfg, key):
                if key in {"screen_width", "screen_height", "max_floors"}:
                    if not isinstance(value, int):
                        raise ValueError(
                            f"{key} must be an integer, got {type(value).__name__}"
                        )
                    if value <= 0:
                        raise ValueError(f"{key} must be greater than 0, got {value}")
                elif key in {"save_file", "score_file"}:
                    if not isinstance(value, str):
                        raise ValueError(
                            f"{key} must be a string, got {type(value).__name__}"
                        )
                elif key == "verbose_combat":
                    if not isinstance(value, bool):
                        raise ValueError(
                            f"{key} must be a boolean, got {type(value).__name__}"
                        )
                setattr(cfg, key, value)
    return cfg


# Load configuration at import so other modules can simply import ``config``.
config = load_config()
