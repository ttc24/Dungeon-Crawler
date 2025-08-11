"""Entry points for running the Dungeon Crawler game.

Character creation now mirrors the progression seen in the source
material: when starting a new run the player only chooses a name.  Class,
race and guild selections are deferred to later floors and offered by the
``DungeonBase`` floor events.
"""

from .dungeon import DungeonBase
from .entities import Player


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
    while True:
        print("1. Start New Game")
        print("2. Load Game")
        print("3. View Leaderboard")
        print("4. Quit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            game.player = build_character()
            game.play_game()
        elif choice == "2":
            game.player = None
            game.play_game()
        elif choice == "3":
            game.view_leaderboard()
        elif choice == "4":
            print("Goodbye!")
            return
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
