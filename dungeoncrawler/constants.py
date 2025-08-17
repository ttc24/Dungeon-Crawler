import json
from functools import lru_cache
from pathlib import Path

from .config import config
from .paths import SAVE_DIR

# Configuration-driven values
# Save files remain in a subdirectory to keep things tidy
SAVE_FILE = SAVE_DIR / config.save_file

# Leaderboard and run statistics are stored alongside saves
SCORE_FILE = SAVE_DIR.parent / config.score_file
# Track how many times the game has been run to provide "Novice's Luck".
RUN_FILE = SAVE_DIR.parent / "run_stats.json"
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
        with open(path, encoding="utf-8") as f:
            riddles = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(riddles, list):
        return []

    normalised: list[dict[str, str]] = []
    for entry in riddles:
        if not isinstance(entry, dict):
            continue
        question = entry.get("question")
        answer = entry.get("answer")
        if not isinstance(question, str) or not isinstance(answer, str):
            continue
        normalised.append({"question": question, "answer": answer.lower()})
    return normalised


# Simple riddles used for trap rooms. Answer correctly to avoid damage.
RIDDLES = load_riddles()
