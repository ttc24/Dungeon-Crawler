# Dungeon Crawler

[![CI](https://github.com/OWNER/Dungeon-Crawler/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/Dungeon-Crawler/actions/workflows/ci.yml)

Dungeon Crawler is a small text-based adventure that borrows the core ideas of the *Dungeon Crawler Carl* where you guide your hero through procedurally generated floors filled with monsters, treasure, and meaningful character choices.

## Quickstart

Clone the repository and start the game with Python 3:

```bash
git clone https://github.com/ttc24/Dungeon-Crawler.git
cd Dungeon-Crawler
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m dungeoncrawler
```

## Installation

The game only requires Python 3. Create a virtual environment, install the dependencies, and run the game using the main module:

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
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
no custom configuration is supplied. When providing your own configuration,
ensure numeric values like `screen_width`, `screen_height`, and `max_floors`
are positive integers—invalid entries will raise a `ValueError` at start-up.

Available configuration options:

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `save_file` | string | `"savegame.json"` | Location of the saved game file. |
| `score_file` | string | `"scores.json"` | Path to the leaderboard data. |
| `max_floors` | int | `18` | Number of dungeon floors to generate. |
| `screen_width` | int | `10` | Width of each dungeon floor in rooms. |
| `screen_height` | int | `10` | Height of each dungeon floor in rooms. |
| `trap_chance` | float | `0.1` | Probability that a room contains a trap. |
| `loot_multiplier` | float | `1.0` | Multiplies the amount of loot found. |
| `verbose_combat` | bool | `false` | Log additional combat details. |
| `enable_debug` | bool | `false` | Toggle extra debug output. |

## Running the Game

When launching the game you start by entering a name. Your class is chosen on
floor one, a guild becomes available on floor two, and races are unlocked on
floor three. Use the number menu to explore rooms, fight monsters, visit
shops, and descend deeper into the dungeon.

At any time you may choose **8. Show Map** to display a grid of the dungeon. The map marks your location with `@`, rooms you've visited with `.`, unexplored or blocked rooms with `#`, and the exit with `E`. While viewing the map, press `?` to toggle a legend of these symbols. Press `q` to return to the game.

Progress is automatically saved whenever you clear a floor. On the next launch you will be asked if you want to continue.

Save data is written to `~/.dungeon_crawler/saves/savegame.json`. The file is a
JSON document containing the current floor and full player state including
statistics, inventory, equipped weapon and companions. High scores are stored in
`scores.json` alongside the save file.

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
