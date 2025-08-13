"""Convenience script for launching the Dungeon Crawler game.

The script simply loads configuration and delegates to
``dungeoncrawler.main.main``.  Keeping this thin wrapper allows the
package entry point and the standalone script to share the same start-up
logic while still supporting ``python dungeon_crawler.py``.
"""

from dungeoncrawler.config import load_config
from dungeoncrawler.main import main

if __name__ == "__main__":
    cfg = load_config()
    main(cfg=cfg)
