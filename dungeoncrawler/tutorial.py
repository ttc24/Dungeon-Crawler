"""Interactive tutorial for basic game mechanics."""

from __future__ import annotations


def run(game) -> None:
    """Run the tutorial sequence.

    The tutorial walks the player through movement, combat and
    inventory management. It relies on simple text prompts that must
    be acknowledged with the appropriate command before moving on to
    the next section.
    """

    print("=== Welcome to the Dungeon Crawler tutorial! ===")
    print("Let's begin with movement. Use '1' (left), '2' (right), '3' (up) or '4' (down).")
    while True:
        move = input("Move: ").strip()
        if move in {"1", "2", "3", "4"}:
            print("Good job! You can navigate the dungeon using those keys.")
            break
        print("Please use one of 1, 2, 3 or 4 to move.")

    print("Now let's practice combat. Type 'attack' to strike the training dummy.")
    while True:
        action = input("Action: ").strip().lower()
        if action == "attack":
            print("The dummy falls apart. A solid hit!")
            break
        print("Type 'attack' to perform an attack.")

    print("Finally, open your inventory by typing 'inventory'.")
    while True:
        action = input("Command: ").strip().lower()
        if action == "inventory":
            print("Your empty bag opens. You'll fill it with loot soon enough.")
            break
        print("Type 'inventory' to check your belongings.")

    print("That's it for the basics. Good luck in the dungeon!")
    game.tutorial_complete = True


if __name__ == "__main__":  # pragma: no cover - convenience script
    from .config import load_config
    from .dungeon import DungeonBase
    from .main import build_character

    cfg = load_config()
    game = DungeonBase(cfg.screen_width, cfg.screen_height)
    game.player = build_character()
    run(game)
