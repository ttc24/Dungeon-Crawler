# Dungeon Crawler

[![CI](https://github.com/ttc24/Dungeon-Crawler/actions/workflows/ci.yml/badge.svg)](https://github.com/ttc24/Dungeon-Crawler/actions/workflows/ci.yml)
![Coverage](coverage.svg)
[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://ttc24.github.io/Dungeon-Crawler/)

Dungeon Crawler is a small text-based adventure that borrows the core ideas of the *Dungeon Crawler Carl* where you guide your hero through procedurally generated floors filled with monsters, treasure, and meaningful character choices.

Full documentation is available in [docs/index.rst](docs/index.rst).

## Quickstart

Clone the repository and start the game with Python 3:

```bash
git clone https://github.com/ttc24/Dungeon-Crawler
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

### Optional Textual Interface

The experimental graphical interface uses the third‑party
[`textual`](https://textual.textualize.io/) framework.  It is not required for
the standard terminal renderer, but you can install it separately to try the
`DungeonApp` showcase:

```bash
pip install textual
```

Make sure the file is executable if you wish to launch it with `./dungeon_crawler.py`.

## Configuration

Game settings are loaded from `config.json` in the project root. Copy the provided
`config.example.json` there and adjust values as needed:

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
| `trap_chance` | float | `0.1` | Probability that a room contains a trap; higher values favor healing fountains on early floors. |
| `enemy_hp_mult` | float | `1.0` | Global multiplier applied to enemy hit points. |
| `enemy_dmg_mult` | float | `1.0` | Global multiplier applied to enemy attack damage. |
| `loot_mult` | float | `1.0` | Multiplies the amount of loot found; higher values favor treasure caches on early floors. |
| `verbose_combat` | bool | `false` | Log additional combat details. |
| `slow_messages` | bool | `false` | Introduce a short delay between message prints. |
| `key_repeat_delay` | float | `0.5` | Time in seconds before held keys repeat. |
| `colorblind_mode` | bool | `false` | Use an alternative palette for improved contrast. |
| `enable_debug` | bool | `false` | Toggle extra debug output. |

## Running the Game

When launching the game you start by entering a name. Your class is chosen on
floor one, a guild becomes available on floor two, and races are unlocked on
floor three. Use the number menu to explore rooms, fight monsters, visit
shops, and descend deeper into the dungeon.

At any time you may choose **8. Show Map** to display a grid of the dungeon. The map marks your location with `@`, the exit with `E`, currently visible rooms with `.`, tiles you've discovered but can't currently see with `·`, and unexplored or blocked rooms with `#`. While viewing the map, press `?` to toggle a legend of these symbols. Press `q` to return to the game.

Progress is automatically saved whenever you clear a floor. On the next launch you will be asked if you want to continue.

Save data is written to `~/.dungeon_crawler/saves/savegame.json`. The file is a
JSON document containing the current floor and full player state including
statistics, inventory, equipped weapon and companions. Save games and leaderboard
entries are written to `~/.dungeon_crawler` in your home directory.

## Objectives

- Survive each floor and defeat the boss to descend.
- Collect powerful weapons and trustworthy companions.
- Rack up the highest score on the in-game leaderboard. Runs can be ranked by
  score, deepest floor reached or fastest completion time.

## Features

- Gradual character creation that unlocks classes, guilds and races as you
  descend.
- Wide class roster including Barbarian, Druid, Ranger, Sorcerer, Monk,
  Warlock, Necromancer, Shaman and Alchemist in addition to classics like
  Warrior and Mage.
- Expanded guild and race options featuring groups such as the Healers'
  Circle or Shadow Brotherhood and races like Tiefling, Dragonborn and
  Goblin.
- Every floor culminates in a unique boss battle. Bosses telegraph their
  attacks and defeating one grants the entire reward table for that encounter.
- Each floor also features exactly one special event drawn from a curated pool—
  like a shrine gauntlet, puzzle chamber or escort mission—to break up the
  routine of boss fights.
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

## Balance Simulation

A small command-line helper can simulate combat to aid balance testing. Run it
against any enemy archetype and tweak the player's stats to model different
classes:

```bash
python -m dungeoncrawler.sim Bandit --runs 100 --player-health 40 --player-attack 10
```

The script reports the win rate and average number of turns taken. The same
interface is available via `scripts/simulate_battles.py`.
