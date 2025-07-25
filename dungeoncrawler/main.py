from .dungeon import DungeonBase


def main():
    game = DungeonBase(10, 10)
    game.play_game()


if __name__ == "__main__":
    main()
