"""Entry points for running the Dungeon Crawler game.

Character creation now mirrors the progression seen in the source
material: when starting a new run the player only chooses a name.  Class,
race and guild selections are deferred to later floors and offered by the
``DungeonBase`` floor events.
"""

import argparse
from gettext import gettext as _

from .config import load_config
from .i18n import set_language


def build_character():
    """Interactively construct a :class:`Player` with just a name.

    Further character customisation happens organically as the player
    explores deeper floors.  This keeps the initial setup light and mirrors
    the gradual progression described in the novels.
    """

    from .entities import Player

    name = ""
    while not name:
        name = input(_("Enter your name: ")).strip()
        if not name:
            print(_("Name cannot be blank."))

    player = Player(name)
    print(_("Welcome {name}! Your journey is just beginning.").format(name=player.name))
    return player


def main(argv=None):
    """Run the game with optional command line arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-tutorial",
        action="store_true",
        help=_("Do not run the interactive tutorial"),
    )
    parser.add_argument("--lang", help=_("Language code for translations"))
    args = parser.parse_args(argv)

    set_language(args.lang)

    global DungeonBase, Player
    from . import combat as combat_module  # noqa: F401
    from . import map as dungeon_map  # noqa: F401
    from . import shop as shop_module  # noqa: F401
    from .dungeon import DungeonBase
    from .entities import Player

    cfg = load_config()
    game = DungeonBase(cfg.screen_width, cfg.screen_height)
    cont = input(_("Load existing save? (y/n): ")).strip().lower()
    if cont != "y":
        game.player = build_character()
        if args.skip_tutorial:
            game.tutorial_complete = True
        elif not game.tutorial_complete:
            from .tutorial import run as run_tutorial

            run_tutorial(game)
    game.play_game()


if __name__ == "__main__":
    main()
