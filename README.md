# Dungeon Crawler

Dungeon Crawler is a small text-based adventure that borrows the core ideas of the *Dungeon Crawler Carl* novels while toning down the humor. Guide your hero through procedurally generated floors filled with monsters, treasure, and meaningful character choices.

## Installation

The game only requires Python 3. Run it directly using the main module:

```bash
python3 -m dungeoncrawler
```

Make sure the file is executable if you wish to launch it with `./dungeon_crawler.py`.

## Running the Game

When launching the game you will first create your hero by choosing a name,
class, race and optionally a guild. Use the number menu to explore rooms,
fight monsters, visit shops, and descend deeper into the dungeon.

Progress is automatically saved whenever you clear a floor. On the next launch you will be asked if you want to continue.

## Objectives

- Survive each floor and defeat the boss to descend.
- Collect powerful weapons and trustworthy companions.
- Rack up the highest score on the in-game leaderboard.

## Features

- Fully fledged character creation with multiple classes, races and guilds.
- Choose from additional classes like Cleric, Paladin and Bard.
- Special floor events add variety as you progress deeper.
- Floors grow in size and feature unique enemy and boss sets.
- Battle through 18 floors of escalating challenge.

## Example

The game can also be driven programmatically:

```python
from dungeoncrawler.main import build_character
from dungeoncrawler.dungeon import DungeonBase

player = build_character()
game = DungeonBase(10, 10)
game.player = player
game.play_game()
```
