from pathlib import Path
import json

# Default save directory under the user's home directory.  Create it on import
# so game code can assume it exists.
SAVE_DIR = Path.home() / ".dungeon_crawler" / "saves"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

SAVE_FILE = SAVE_DIR / "savegame.json"
SCORE_FILE = SAVE_DIR / "scores.json"
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
