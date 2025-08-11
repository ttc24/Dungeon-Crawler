from pathlib import Path
import json
from functools import lru_cache

from .config import config

# Configuration-driven values
SAVE_FILE = config.save_file
SCORE_FILE = config.score_file
MAX_FLOORS = config.max_floors
SCREEN_WIDTH = config.screen_width
SCREEN_HEIGHT = config.screen_height
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
    with open(path) as f:
        riddles = json.load(f)
    # Normalise answers for case-insensitive comparison
    for r in riddles:
        r["answer"] = r["answer"].lower()
    return riddles


# Simple riddles used for trap rooms. Answer correctly to avoid damage.
RIDDLES = load_riddles()
