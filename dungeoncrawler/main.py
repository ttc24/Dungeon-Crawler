"""Entry points for running the Dungeon Crawler game.

This module now supports a full character creation flow via
``build_character`` which prompts the player for a name, class, race and
guild before the game begins.
"""

from .dungeon import DungeonBase
from .entities import Player


def _prompt_choice(prompt, options):
    """Prompt the user until a valid option key is entered."""

    while True:
        choice = input(prompt).strip()
        if choice in options:
            return options[choice]
        print("Invalid choice. Please try again.")


def build_character():
    """Interactively construct a :class:`Player`.

    The function validates user input for each step and returns a fully
    initialised ``Player`` instance.
    """

    name = ""
    while not name:
        name = input("Enter your name: ").strip()
        if not name:
            print("Name cannot be blank.")

    classes = {
        "1": "Warrior",
        "2": "Mage",
        "3": "Rogue",
        "4": "Cleric",
        "5": "Paladin",
        "6": "Bard",
    }
    class_type = _prompt_choice(
        "Choose your class: 1. Warrior 2. Mage 3. Rogue 4. Cleric 5. Paladin 6. Bard\nClass: ",
        classes,
    )

    player = Player(name, class_type)

    races = {
        "1": "Human",
        "2": "Elf",
        "3": "Dwarf",
        "4": "Orc",
        "5": "Gnome",
        "6": "Halfling",
        "7": "Catfolk",
        "8": "Lizardfolk",
    }
    race = _prompt_choice(
        "Choose your race: 1. Human 2. Elf 3. Dwarf 4. Orc 5. Gnome 6. Halfling 7. Catfolk 8. Lizardfolk\nRace: ",
        races,
    )
    player.choose_race(race)

    guilds = {
        "1": "Warriors' Guild",
        "2": "Mages' Guild",
        "3": "Rogues' Guild",
        "4": None,
    }
    guild = _prompt_choice(
        "Join a guild? 1. Warriors' Guild 2. Mages' Guild 3. Rogues' Guild 4. None\nGuild: ",
        guilds,
    )
    if guild:
        player.join_guild(guild)

    print(f"Welcome {player.name} the {player.class_type}!")
    return player


def main():
    game = DungeonBase(10, 10)
    cont = input("Load existing save? (y/n): ").strip().lower()
    if cont != "y":
        game.player = build_character()
    game.play_game()


if __name__ == "__main__":
    main()
