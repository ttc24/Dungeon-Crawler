"""Allow ``python -m dungeoncrawler`` to launch the game.

This module mirrors the behaviour of the standalone ``dungeon_crawler.py``
script by loading configuration before delegating to :func:`main`.
"""

from .config import load_config
from .main import main as run_game


def main() -> None:
    """Load configuration and launch the game loop."""
    cfg = load_config()
    run_game(cfg=cfg)


if __name__ == "__main__":
    main()
