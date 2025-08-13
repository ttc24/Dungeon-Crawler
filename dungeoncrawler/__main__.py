"""Allow ``python -m dungeoncrawler`` to launch the game.

This module mirrors the behaviour of the standalone ``dungeon_crawler.py``
script by loading configuration before delegating to :func:`main`.
"""

from .config import load_config
from .main import main


if __name__ == "__main__":
    cfg = load_config()
    main(cfg=cfg)
