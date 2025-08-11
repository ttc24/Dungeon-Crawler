"""Map generation and navigation utilities."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .entities import Companion, Enemy
from .items import Item, Weapon
from .combat import battle

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from .dungeon import DungeonBase


def generate_dungeon(game: "DungeonBase", floor: int = 1) -> None:
    """Populate the dungeon layout for ``floor``."""

    cfg = game.floor_configs.get(floor)
    if cfg is None:
        raise ValueError(f"Floor {floor} is not configured")
    size = cfg.get("size", (min(15, 8 + floor), min(15, 8 + floor)))
    game.width, game.height = size
    game.rooms = [[None for _ in range(game.width)] for _ in range(game.height)]
    game.room_names = [
        [game.generate_room_name() for _ in range(game.width)]
        for _ in range(game.height)
    ]
    visited = set()
    path = []
    x, y = game.width // 2, game.height // 2
    start = (x, y)
    visited.add(start)
    path.append(start)

    while len(visited) < (game.width * game.height) // 2:
        direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        nx, ny = x + direction[0], y + direction[1]
        if 0 <= nx < game.width and 0 <= ny < game.height:
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                path.append((nx, ny))
            x, y = nx, ny

    for x, y in visited:
        game.rooms[y][x] = "Empty"

    if game.player is None:
        raise ValueError("Player must be created before generating the dungeon.")
    game.rooms[start[1]][start[0]] = game.player
    game.player.x, game.player.y = start
    game.visited_rooms.add(start)

    visited.remove(start)
    visited = list(visited)
    random.shuffle(visited)

    def place(obj):
        if visited:
            px, py = visited.pop()
            game.rooms[py][px] = obj
            return (px, py)

    game.exit_coords = place("Exit")
    place(Item("Key", "Opens the dungeon exit"))

    enemy_names = cfg["enemies"]
    early_game_bonus = 5 if floor <= 3 else 0
    for _ in range(5 + floor):
        name = random.choice(enemy_names)
        hp_min, hp_max, atk_min, atk_max, defense = game.enemy_stats[name]

        hp_scale = 1 if floor <= 3 else 2
        atk_scale = 1 if floor <= 3 else 2

        defense = max(1, defense + floor // 3)

        health = random.randint(
            hp_min + floor * hp_scale, hp_max + floor * hp_scale
        )
        attack = random.randint(
            atk_min + floor * atk_scale,
            atk_max + floor * atk_scale,
        )
        gold = random.randint(15 + early_game_bonus + floor, 30 + floor * 2)

        ability = game.enemy_abilities.get(name)
        enemy = Enemy(name, health, attack, defense, gold, ability)
        enemy.xp = max(5, (health + attack + defense) // 15)

        place(enemy)

    boss_names = cfg["bosses"]
    name = random.choice(boss_names)
    hp, atk, dfs, gold, ability = game.boss_stats[name]
    print(f"A powerful boss guards this floor! The {name} lurks nearby...")
    boss = Enemy(
        name,
        hp + floor * 10,
        atk + floor,
        dfs + floor // 2,
        gold + floor * 5,
        ability=ability,
    )
    place(boss)
    boss_drop = game.boss_loot.get(name, [])
    if boss_drop and random.random() < 0.5:
        loot = random.choice(boss_drop)
        print(f"✨ The boss dropped a unique weapon: {loot.name}!")
        place(loot)

    place(Item("Key", "A magical key dropped by the boss"))
    companion_options = [
        Companion("Battle Priest", "heal"),
        Companion("Hired Blade", "attack"),
    ]
    place(random.choice(companion_options))
    default_places = {
        "Trap": 3,
        "Treasure": 3,
        "Enchantment": 2,
        "Sanctuary": 2,
        "Blacksmith": 1,
    }
    place_counts = default_places.copy()
    place_counts.update(cfg.get("places", {}))
    for pname, count in place_counts.items():
        for _ in range(count):
            place(pname)
    # Key is now tied to boss drop; don't place it separately


def move_player(game: "DungeonBase", direction: str) -> None:
    """Move the player if the target tile is valid."""

    dx, dy = {"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}.get(
        direction, (0, 0)
    )
    x, y = game.player.x + dx, game.player.y + dy
    if 0 <= x < game.width and 0 <= y < game.height and game.rooms[y][x] is not None:
        handle_room(game, x, y)
    else:
        print("You can't move that way.")


def render_map(game: "DungeonBase") -> None:
    """Render a simple textual representation of the map."""

    for y in range(game.height):
        row = ""
        for x in range(game.width):
            pos = (x, y)
            if pos == (game.player.x, game.player.y):
                row += "@"
            elif pos in game.visited_rooms or pos == game.exit_coords:
                row += "."
            else:
                row += "#"
        print(row)


def handle_room(game: "DungeonBase", x: int, y: int) -> None:
    """Execute logic for entering a room at ``x``, ``y``."""

    room = game.rooms[y][x]
    name = game.room_names[y][x]
    lore = {
        "Glittering Vault": "The air shimmers with unseen magic. Ancient riches may lie within.",
        "Booby-Trapped Passage": "This corridor is riddled with pressure plates and crumbled bones.",
        "Cursed Hall": "The shadows shift... something watches from the dark.",
        "Sealed Gate": "Massive stone doors sealed by arcane runes. It might be the only way out.",
        "Hidden Niche": "A hollow carved into the wall, forgotten by time. Something valuable glints inside.",
        "Silent Chamber": "Dust covers everything. It appears long abandoned.",
        "Sacred Sanctuary": "A peaceful place that heals weary adventurers.",
    }
    if name in lore:
        print(f"{lore[name]}")

    if isinstance(room, Enemy):
        battle(game, room)
        if not room.is_alive():
            game.rooms[y][x] = None
    elif isinstance(room, Companion):
        print(f"You meet {room.name}. {room.description}")
        recruit = input("Recruit this companion? (y/n): ")
        if recruit.lower() == "y":
            game.player.companions.append(room)
            if room.effect == "attack":
                game.player.attack_power += 2
            elif room.effect == "heal":
                game.player.max_health += 5
                game.player.health += 5
            game.announce(f"{game.player.name} gains a companion!")
        game.rooms[y][x] = None
    elif isinstance(room, Item):
        print(f"You found a {room.name}!")
        game.player.collect_item(room)
        game.announce(f"{game.player.name} obtained {room.name}!")
        game.rooms[y][x] = None
        if room.name == "Key":
            game.room_names[y][x] = "Hidden Niche"
    elif room == "Treasure":
        gold = random.randint(20, 50)
        game.player.gold += gold
        print(f"You found a treasure chest with {gold} gold!")
        if random.random() < 0.3:
            loot = random.choice(game.rare_loot)
            print(f"Inside you also discover {loot.name}!")
            game.player.collect_item(loot)
            game.announce(f"{game.player.name} picks up {loot.name}!")
        game.rooms[y][x] = None
        game.room_names[y][x] = "Glittering Vault"
    elif room == "Enchantment":
        print("You enter a glowing chamber with ancient runes etched in the stone.")
        if game.player.weapon:
            print(f"Your current weapon is: {game.player.weapon.name}")
            print("You may enchant it with a status effect for 30 gold.")
            print("1. Poison  2. Burn  3. Freeze  4. Cancel")
            choice = input("Choose enchantment: ")
            if game.player.weapon.effect:
                print("Your weapon is already enchanted! You can't add another enchantment.")
            elif game.player.gold >= 30 and choice in ["1", "2", "3"]:
                effect = {"1": "poison", "2": "burn", "3": "freeze"}[choice]
                game.player.weapon.description += f" (Enchanted: {effect})"
                game.player.weapon.effect = effect
                game.player.gold -= 30
                print(f"Your weapon is now enchanted with {effect}!")
            elif choice == "4":
                print("You leave the enchantment chamber untouched.")
            else:
                print("Not enough gold or invalid choice.")
        else:
            print("You need a weapon to enchant.")
        game.rooms[y][x] = None
        game.room_names[y][x] = "Enchantment Chamber"
    elif room == "Blacksmith":
        print("You meet a grizzled blacksmith hammering at a forge.")
        if game.player.weapon:
            print(
                f"Your weapon: {game.player.weapon.name} ({game.player.weapon.min_damage}-{game.player.weapon.max_damage})"
            )
            print("Would you like to upgrade your weapon for 50 gold? +3 min/max damage")
            confirm = input("Upgrade? (y/n): ")
            if confirm.lower() == "y" and game.player.gold >= 50:
                game.player.weapon.min_damage += 3
                game.player.weapon.max_damage += 3
                game.player.gold -= 50
                print("Your weapon has been reforged and is stronger!")
            elif game.player.gold < 50:
                print("You don't have enough gold.")
            else:
                print("Maybe next time.")
        else:
            print(
                "The blacksmith scoffs. 'No weapon? Come back when you have something worth forging.'"
            )
        game.rooms[y][x] = None
        game.room_names[y][x] = "Blacksmith Forge"

    elif room == "Sanctuary":
        game.player.health = game.player.max_health
        print("A soothing warmth envelops you. Your wounds are fully healed.")
        game.rooms[y][x] = None
        game.room_names[y][x] = "Sacred Sanctuary"

    elif room == "Trap":
        riddle = random.choice(game.riddles)
        print("A trap springs! Solve this riddle to escape unharmed:")
        print(riddle["question"])
        response = input("Answer: ").strip().lower()
        if response == riddle["answer"].lower():
            print("The mechanism clicks harmlessly. You solved it!")
            game.announce("Brilliant puzzle solving!")
        else:
            damage = random.randint(10, 30)
            game.player.take_damage(damage)
            print(f"Wrong answer! You take {damage} damage.")
        game.rooms[y][x] = None
        game.room_names[y][x] = "Booby-Trapped Passage"
    elif room == "Exit":
        game.room_names[y][x] = "Sealed Gate"
        if game.player.has_item("Key"):
            print("🎉 You unlocked the exit and escaped the dungeon!")
            print(f"Final Score: {game.player.get_score()}")
            exit()
        else:
            print("The exit is locked. You need a key!")

    game.rooms[game.player.y][game.player.x] = None
    game.player.x, game.player.y = x, y
    game.rooms[y][x] = game.player
    game.visited_rooms.add((x, y))
    game.audience_gift()

