import json
from functools import lru_cache
from pathlib import Path

from .config import config

# Configuration-driven values
# Base directory for all persistent data
BASE_DIR = Path.home() / ".dungeon_crawler"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Save files remain in a subdirectory to keep things tidy
SAVE_DIR = BASE_DIR / "saves"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
SAVE_FILE = SAVE_DIR / config.save_file

# Leaderboard is stored directly in ``~/.dungeon_crawler``
SCORE_FILE = BASE_DIR / config.score_file
# Track how many times the game has been run to provide "Novice's Luck".
RUN_FILE = BASE_DIR / "run_stats.json"
MAX_FLOORS = config.max_floors
SCREEN_WIDTH = config.screen_width
SCREEN_HEIGHT = config.screen_height
INVALID_KEY_MSG = "Unknown key. Try [WASD] to move, [F] to defend, [G] to grab."
ANNOUNCER_LINES = [
    "A decisive blow!",
    "You fight with determination.",
    "Your skill improves.",
    "You press the attack.",
    "The crowd goes wild!",
    "Fans cheer from across the stars.",
    "Viewers gasp in suspense.",
    "Our ratings just spiked!",
    "Another thrilling moment for our contestant.",
]


@lru_cache(maxsize=None)
def load_riddles():
    """Load riddles from the JSON data file.

    The file is expected to contain a list of objects with ``question`` and
    ``answer`` fields.  Answers are stored in lower case for easy
    comparisons during gameplay.
    """

    data_dir = Path(__file__).resolve().parent.parent / "data"
    path = data_dir / "riddles.json"
    try:
        with open(path) as f:
            riddles = json.load(f)
    except (IOError, json.JSONDecodeError):
        return []
    # Normalise answers for case-insensitive comparison
    for r in riddles:
        r["answer"] = r["answer"].lower()
    return riddles


# Simple riddles used for trap rooms. Answer correctly to avoid damage.
RIDDLES = load_riddles()
