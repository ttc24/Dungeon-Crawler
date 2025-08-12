# Modding the Dungeon Crawler

The game now supports lightweight plug-ins that can extend enemies and items.
Mods live inside the top level `mods/` package.  Each mod is a normal Python
package placed in its own subdirectory, e.g. `mods/my_mod/`.

```
mods/
└── my_mod/
    ├── __init__.py
    └── data/
        ├── enemies.json  # optional
        └── items.json    # optional
```

## Plugin hooks

A mod can expose two optional functions in its `__init__` module:

```python
# mods/my_mod/__init__.py
from dungeoncrawler.items import Weapon

def register_enemies(enemy_stats, enemy_abilities):
    enemy_stats["Gelatinous Cube"] = (30, 5, 8, 12, 2)
    enemy_abilities["Gelatinous Cube"] = "dissolve"

def register_items(shop_items):
    shop_items.append(Weapon("Rusty Pike", "Barely holds together", 3, 6, 5))
```

`register_enemies` receives the global enemy dictionaries and can add new
entries.  `register_items` is handed the list of shop items used when the game
starts.

## Supplying JSON data

Instead of using Python hooks, mods may ship JSON files.  Place them in a
`data` directory inside the mod:

- `enemies.json` follows the same schema as the built-in `data/enemies.json`.
- `items.json` can contain two lists: `weapons` and `items`, each with the
  appropriate fields for `Weapon` or `Item` objects.

These files are automatically discovered and merged into the game's data during
initialisation.

After creating your mod, launch the game normally and it will automatically
load any modules found under `mods/`.
