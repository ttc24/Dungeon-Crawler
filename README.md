# Dungeon Crawler

Dungeon Crawler is a small text-based adventure that borrows the core ideas of the *Dungeon Crawler Carl* novels while toning down the humor. Guide your hero through procedurally generated floors filled with monsters, treasure, and meaningful character choices.

## Installation

The game only requires Python 3. Run it directly using the main module:

```bash
python3 -m dungeoncrawler
```

Make sure the file is executable if you wish to launch it with `./dungeon_crawler.py`.

## Running the Game

You will be prompted for a character name. Use the number menu to explore rooms, fight monsters, visit shops, and descend deeper into the dungeon.

At any time you may choose **8. Show Map** to display a grid of the dungeon. The map marks your location with `@`, rooms you've visited with `.`, and unexplored or blocked rooms with `#`.

Progress is automatically saved whenever you clear a floor. On the next launch you will be asked if you want to continue.

## Objectives

- Survive each floor and defeat the boss to descend.
- Collect powerful weapons and trustworthy companions.
- Rack up the highest score on the in-game leaderboard.

## Features

- Join a guild starting on the second floor to gain unique bonuses.
- Unlock new playable races when reaching the third floor.
- Choose from additional classes like Cleric, Paladin and Bard.
- Special floor events add variety as you progress deeper.
- Floors grow in size and feature unique enemy and boss sets.
- Battle through 18 floors of escalating challenge.


<<<<<<< codex/add-render_map-method-in-dungeonbase
- View an ASCII map of explored rooms to track your progress.
=======

## Data Files

Enemy and boss definitions are stored in JSON under the `data/` directory. The game loads these files at runtime:

- `data/enemies.json` – maps enemy names to a `stats` array `[hp_min, hp_max, atk_min, atk_max, defense]` and an optional `ability` field.
- `data/bosses.json` – maps boss names to `stats` `[hp, atk, defense, gold]`, an optional `ability`, and optional `loot` lists containing weapon attributes (`name`, `description`, `min_damage`, `max_damage`, `price`).

Modifying these files allows tweaking the game's combat balance or adding new foes without touching the core code.
>>>>>>> main

