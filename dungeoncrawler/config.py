from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


@dataclass
class Config:
    """Game configuration loaded from ``config.json``.

    Besides basic layout settings such as ``screen_width`` and
    ``screen_height`` the configuration also exposes gameplay toggles like
    ``trap_chance`` and several multipliers that affect overall balance.  The
    ``enemy_hp_mult`` and ``enemy_dmg_mult`` values allow quick adjustment of
    monster statistics while ``loot_mult`` scales treasure gains.  Default
    values mirror the previous hard-coded constants so the game remains
    playable even if no configuration file is provided.
    """

    save_file: str = "savegame.json"
    score_file: str = "scores.json"
    max_floors: int = 18
    screen_width: int = 10
    screen_height: int = 10
    verbose_combat: bool = False
    slow_messages: bool = False
    key_repeat_delay: float = 0.5
    colorblind_mode: bool = False
    trap_chance: float = 0.1
    enemy_hp_mult: float = 1.0
    enemy_dmg_mult: float = 1.0
    loot_mult: float = 1.0
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
            data: Any = json.loads(path.read_text())
        except json.JSONDecodeError:
            return cfg
        if not isinstance(data, dict):
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
                elif key in {"verbose_combat", "enable_debug", "slow_messages", "colorblind_mode"}:
                    if not isinstance(value, bool):
                        raise ValueError(f"{key} must be a boolean, got {type(value).__name__}")
                elif key == "trap_chance":
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"{key} must be a number, got {type(value).__name__}")
                    if not 0 <= float(value) <= 1:
                        raise ValueError(f"{key} must be between 0 and 1, got {value}")
                    value = float(value)
                elif key in {"loot_mult", "enemy_hp_mult", "enemy_dmg_mult", "loot_multiplier"}:
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"{key} must be a number, got {type(value).__name__}")
                    if float(value) <= 0:
                        raise ValueError(f"{key} must be greater than 0, got {value}")
                    value = float(value)
                    key = "loot_mult" if key == "loot_multiplier" else key
                elif key == "key_repeat_delay":
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"{key} must be a number, got {type(value).__name__}")
                    if float(value) < 0:
                        raise ValueError(f"{key} must be greater than or equal to 0, got {value}")
                    value = float(value)
                setattr(cfg, key, value)
            else:
                cfg.extras[key] = value
    return cfg


def save_config(cfg: Config, path: Path = CONFIG_PATH) -> None:
    """Persist ``cfg`` to ``path``.

    Parameters
    ----------
    cfg:
        Configuration instance to serialize.
    path:
        Destination for the JSON file. Defaults to ``config.json`` in the
        project root.
    """

    data = {k: getattr(cfg, k) for k in cfg.__dataclass_fields__ if k != "extras"}
    if cfg.extras:
        data.update(cfg.extras)
    path.write_text(json.dumps(data, indent=2))


def settings_menu(
    cfg: Config,
    path: Path = CONFIG_PATH,
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> Config:
    """Interactively adjust configuration values.

    The menu prompts the user for each supported setting. Pressing Enter keeps
    the current value. Updated settings are written to ``path`` before the
    updated configuration is returned.
    """

    output_func("Configure game settings. Press Enter to keep current values.")
    prompts: list[tuple[str, Callable[[str], Any]]] = [
        ("screen_width", int),
        ("screen_height", int),
        ("trap_chance", float),
        ("enemy_hp_mult", float),
        ("enemy_dmg_mult", float),
        ("loot_mult", float),
        (
            "colorblind_mode",
            lambda s: s.strip().lower() in {"y", "yes", "true", "1"},
        ),
    ]

    for key, caster in prompts:
        current = getattr(cfg, key)
        raw = input_func(f"{key.replace('_', ' ').title()} [{current}]: ").strip()
        if not raw:
            continue
        try:
            value = caster(raw)
        except ValueError:
            output_func(f"Invalid value for {key!r}; keeping {current}.")
            continue
        valid = True
        if key in {"screen_width", "screen_height"}:
            valid = isinstance(value, int) and value > 0
        elif key == "trap_chance":
            valid = isinstance(value, (int, float)) and 0 <= float(value) <= 1
        elif key in {"enemy_hp_mult", "enemy_dmg_mult", "loot_mult"}:
            valid = isinstance(value, (int, float)) and float(value) > 0
        if not valid:
            output_func(f"Invalid value for {key!r}; keeping {current}.")
            continue
        setattr(cfg, key, value)

    save_config(cfg, path)
    return cfg


# Load configuration at import so other modules can simply import ``config``.
config = load_config()
