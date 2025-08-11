"""Entry points for running the Dungeon Crawler game.

Character creation now mirrors the progression seen in the source
material: when starting a new run the player only chooses a name.  Class,
race and guild selections are deferred to later floors and offered by the
``DungeonBase`` floor events.

This module also wires up the optional tutorial which introduces basic
gameplay concepts before the first adventure.
"""

from .dungeon import DungeonBase
from .entities import Player
from .tutorial import run_tutorial
import argparse


def build_character():
    """Interactively construct a :class:`Player` with just a name.

    Further character customisation happens organically as the player
    explores deeper floors.  This keeps the initial setup light and mirrors
    the gradual progression described in the novels.
    """

    name = ""
    while not name:
        name = input("Enter your name: ").strip()
        if not name:
            print("Name cannot be blank.")

    player = Player(name)
    print(f"Welcome {player.name}! Your journey is just beginning.")
    return player


def main(args=None):
    """Launch the game optionally running the tutorial.

    Parameters
    ----------
    args: list[str] | None
        Optional list of arguments. When ``None`` the values from
        ``sys.argv`` are used.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-tutorial",
        action="store_true",
        help="Skip the introductory tutorial",
    )
    opts = parser.parse_args(args)

    game = DungeonBase(10, 10)
    cont = input("Load existing save? (y/n): ").strip().lower()
    if cont != "y":
        game.player = build_character()
        if not opts.skip_tutorial:
            run_tutorial(game.player)
        game.tutorial_complete = True
    game.play_game()


if __name__ == "__main__":
    main()
