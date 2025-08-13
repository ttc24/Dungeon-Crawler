from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


@dataclass
class Config:
    """Game configuration loaded from ``config.json``.

    Besides basic layout settings such as ``screen_width`` and
    ``screen_height`` the configuration also exposes gameplay toggles like
    ``trap_chance``, ``loot_multiplier`` and ``verbose_combat``.  Default
    values mirror the previous hard-coded constants so the game remains
    playable even if no configuration file is provided.
    """

    save_file: str = "savegame.json"
    score_file: str = "scores.json"
    max_floors: int = 18
    screen_width: int = 10
    screen_height: int = 10
    verbose_combat: bool = False
    trap_chance: float = 0.1
    loot_multiplier: float = 1.0
    enable_debug: bool = False
    extras: dict[str, Any] = field(default_factory=dict)


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
        accepted range. For example ``screen_width`` and ``max_floors`` must be
        positive integers.
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
                        raise ValueError(f"{key} must be an integer, got {type(value).__name__}")
                    if value <= 0:
                        raise ValueError(f"{key} must be greater than 0, got {value}")
                elif key in {"save_file", "score_file"}:
                    if not isinstance(value, str):
                        raise ValueError(f"{key} must be a string, got {type(value).__name__}")
                elif key in {"verbose_combat", "enable_debug"}:
                    if not isinstance(value, bool):
                        raise ValueError(f"{key} must be a boolean, got {type(value).__name__}")
                elif key == "trap_chance":
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"{key} must be a number, got {type(value).__name__}")
                    if not 0 <= float(value) <= 1:
                        raise ValueError(f"{key} must be between 0 and 1, got {value}")
                    value = float(value)
                elif key == "loot_multiplier":
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"{key} must be a number, got {type(value).__name__}")
                    if float(value) <= 0:
                        raise ValueError(f"{key} must be greater than 0, got {value}")
                    value = float(value)
                setattr(cfg, key, value)
            else:
                cfg.extras[key] = value
    return cfg


# Load configuration at import so other modules can simply import ``config``.
config = load_config()
