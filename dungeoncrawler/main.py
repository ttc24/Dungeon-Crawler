"""Entry points for running the Dungeon Crawler game.

Character creation now mirrors the progression seen in the source
material: when starting a new run the player only chooses a name.  Class,
race and guild selections are deferred to later floors and offered by the
``DungeonBase`` floor events.
"""

from .dungeon import DungeonBase
from .entities import Player
# Import modules to expose new separation of concerns (unused in CLI but
# required by tests and for side effects).
from . import combat as _combat  # noqa: F401
from . import map as _map  # noqa: F401
from . import shop as _shop  # noqa: F401


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


def main():
    game = DungeonBase(10, 10)
    cont = input("Load existing save? (y/n): ").strip().lower()
    if cont != "y":
        game.player = build_character()
    game.play_game()


if __name__ == "__main__":
    main()
