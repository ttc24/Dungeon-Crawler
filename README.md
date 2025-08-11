# Dungeon Crawler

[![CI](https://github.com/OWNER/Dungeon-Crawler/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/Dungeon-Crawler/actions/workflows/ci.yml)

Dungeon Crawler is a small text-based adventure that borrows the core ideas of the *Dungeon Crawler Carl* novels while toning down the humor. Guide your hero through procedurally generated floors filled with monsters, treasure, and meaningful character choices.

## Installation

The game only requires Python 3. Run it directly using the main module:

```bash
python3 -m dungeoncrawler
```

Make sure the file is executable if you wish to launch it with `./dungeon_crawler.py`.

## Configuration

Game settings are loaded from `config.json` if present. Copy the provided
`config.example.json` and adjust values as needed:

```bash
cp config.example.json config.json
```

The defaults mirror previous hard-coded values so the game will run even if
no custom configuration is supplied.

## Running the Game

When launching the game you start by entering a name. Your class is chosen on
floor one, a guild becomes available on floor two, and races are unlocked on
floor three. Use the number menu to explore rooms, fight monsters, visit
shops, and descend deeper into the dungeon.

At any time you may choose **8. Show Map** to display a grid of the dungeon. The map marks your location with `@`, rooms you've visited with `.`, and unexplored or blocked rooms with `#`.

Progress is automatically saved whenever you clear a floor. On the next launch you will be asked if you want to continue.

## Objectives

- Survive each floor and defeat the boss to descend.
- Collect powerful weapons and trustworthy companions.
- Rack up the highest score on the in-game leaderboard.

## Features

- Gradual character creation that unlocks classes, guilds and races as you
  descend.
- Wide class roster including Barbarian, Druid, Ranger, Sorcerer, Monk,
  Warlock, Necromancer, Shaman and Alchemist in addition to classics like
  Warrior and Mage.
- Expanded guild and race options featuring groups such as the Healers'
  Circle or Shadow Brotherhood and races like Tiefling, Dragonborn and
  Goblin.
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
