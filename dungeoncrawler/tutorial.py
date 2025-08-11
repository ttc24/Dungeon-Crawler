"""Simple interactive tutorial for basic gameplay concepts."""


def run_tutorial(player):
    """Guide the player through movement, combat and inventory basics."""
    print("--- Tutorial: Movement ---")
    input("Use WASD keys to move your character. Press Enter to continue...")

    print("--- Tutorial: Combat ---")
    input("Combat is turn-based. Press Enter to strike at your foe...")

    print("--- Tutorial: Inventory ---")
    input("Open your inventory with 'i'. Press Enter once you've looked around...")

    print("You're ready to begin your adventure, brave {}!".format(player.name))
