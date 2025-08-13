"""Map generation and navigation utilities."""

from __future__ import annotations

import random
from collections import deque
from gettext import gettext as _
from typing import TYPE_CHECKING

from .ai import IntentAI
from .combat import battle
from .data import load_companions
from .entities import Companion, Enemy
from .events import BaseEvent, CacheEvent, FountainEvent
from .flavor import generate_room_flavor
from .items import Item
from .quests import EscortNPC
from .rendering import render_map_string

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from .dungeon import DungeonBase


def compute_visibility(grid, px, py, radius):
    """Return set of visible tiles using BFS from ``(px, py)``."""

    height = len(grid)
    width = len(grid[0]) if height else 0
    visited = set()
    queue = deque([(px, py, 0)])
    while queue:
        x, y, dist = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if dist >= radius:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] is not None:
                queue.append((nx, ny, dist + 1))
    return visited


def update_visibility(game: "DungeonBase") -> None:
    """Recompute visible and discovered tiles for ``game``."""

    game.visible = [[False for __ in range(game.width)] for __ in range(game.height)]
    radius = 6 if game.current_floor == 1 else 3 + game.current_floor // 2
    for x, y in compute_visibility(game.rooms, game.player.x, game.player.y, radius):
        game.visible[y][x] = True
        game.discovered[y][x] = True


def generate_dungeon(game: "DungeonBase", floor: int = 1) -> None:
    """Populate the dungeon layout for ``floor``."""

    cfg = game.floor_configs.get(floor)
    if cfg is None:
        raise ValueError(f"Floor {floor} is not configured")
    size = cfg.get("size", (min(15, 8 + floor), min(15, 8 + floor)))
    game.width, game.height = size
    game.current_floor = floor
    # Determine if the first-run bonus applies
    game.player.novice_luck_active = game.total_runs == 0 and floor <= 2
    if game.player.novice_luck_active and not game.novice_luck_announced:
        game.queue_message(_("You feel emboldened (Novice's Luck)."))
        game.novice_luck_announced = True
    game.rooms = [[None for __ in range(game.width)] for __ in range(game.height)]
    game.room_names = [
        [game.generate_room_name() for __ in range(game.width)] for __ in range(game.height)
    ]
    game.discovered = [[False for __ in range(game.width)] for __ in range(game.height)]
    game.visible = [[False for __ in range(game.width)] for __ in range(game.height)]
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

    def place_near_start(obj, max_dist):
        candidates = [
            pos for pos in visited if abs(pos[0] - start[0]) + abs(pos[1] - start[1]) <= max_dist
        ]
        random.shuffle(candidates)
        if candidates:
            px, py = candidates.pop()
            visited.remove((px, py))
            game.rooms[py][px] = obj
            return (px, py)
        return place(obj)

    if floor == 1:
        game.exit_coords = place_near_start("Exit", 4)
    else:
        game.exit_coords = place("Exit")
    place(Item("Key", "Opens the dungeon exit"))
    if floor == 1:
        place_near_start("Sanctuary", 10)

    enemy_names = cfg["enemies"]
    early_game_bonus = 5 if floor <= 3 else 0
    walkable = (game.width * game.height) // 2
    density_map = {1: (3, 4), 2: (5, 6), 3: (7, 8)}
    low, high = density_map.get(floor, (8, 9))
    enemy_total = max(1, walkable * random.randint(low, high) // 100)
    for __ in range(enemy_total):
        name = random.choice(enemy_names)
        hp_min, hp_max, atk_min, atk_max, defense = game.enemy_stats[name]

        hp_scale = 1 if floor <= 3 else 2
        atk_scale = 1 if floor <= 3 else 2

        defense = max(1, defense + floor // 3)

        health = random.randint(hp_min + floor * hp_scale, hp_max + floor * hp_scale)
        attack = random.randint(
            atk_min + floor * atk_scale,
            atk_max + floor * atk_scale,
        )
        gold = random.randint(15 + early_game_bonus + floor, 30 + floor * 2)

        ability = game.enemy_abilities.get(name)
        weights = game.enemy_ai.get(name)
        ai = IntentAI(**weights) if weights else None
        enemy = Enemy(name, health, attack, defense, gold, ability, ai)
        enemy.xp = max(5, (health + attack + defense) // 15)

        place(enemy)

    boss_names = cfg["bosses"]
    name = random.choice(boss_names)
    hp, atk, dfs, gold, ability = game.boss_stats[name]
    game.queue_message(_(f"A powerful boss guards this floor! The {name} lurks nearby..."))
    boss_weights = game.boss_ai.get(name)
    boss_ai = IntentAI(**boss_weights) if boss_weights else None
    boss = Enemy(
        name,
        hp + floor * 10,
        atk + floor,
        dfs + floor // 2,
        gold + floor * 5,
        ability=ability,
        ai=boss_ai,
    )
    place(boss)
    boss_drop = game.boss_loot.get(name, [])
    if boss_drop and random.random() < 0.5:
        loot = random.choice(boss_drop)
        game.queue_message(_(f"✨ The boss dropped a unique weapon: {loot.name}!"))
        place(loot)

    place(Item("Key", "A magical key dropped by the boss"))
    companion_options = load_companions()
    place(random.choice(companion_options))
    if floor <= 3:
        place(FountainEvent())
        place(CacheEvent())
    place_counts = game.default_place_counts.copy()
    place_counts.update(cfg.get("places", {}))
    for pname, count in place_counts.items():
        for __ in range(count):
            place(pname)

    if floor == 1:
        # Guarantee an uncommon item on the first floor
        place(random.choice(game.rare_loot))
    # Key is now tied to boss drop; don't place it separately

    update_visibility(game)


def move_player(game: "DungeonBase", direction: str) -> None:
    """Move the player if the target tile is valid."""

    dx, dy = {"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}.get(
        direction, (0, 0)
    )
    x, y = game.player.x + dx, game.player.y + dy
    if 0 <= x < game.width and 0 <= y < game.height and game.rooms[y][x] is not None:
        handle_room(game, x, y)
        update_visibility(game)
    else:
        return game.queue_message(_("You can't move that way."))


def handle_room(game: "DungeonBase", x: int, y: int) -> None:
    """Execute logic for entering a room at ``x``, ``y``."""

    room = game.rooms[y][x]
    name = game.room_names[y][x]
    flavor = generate_room_flavor(name)
    if flavor:
        game.queue_message(flavor)

    if isinstance(room, list):
        for obj in list(room):
            if isinstance(obj, BaseEvent):
                obj.trigger(game, output_func=game.queue_message)
            elif isinstance(obj, Item):
                game.queue_message(_(f"You found a {obj.name}!"))
                game.player.collect_item(obj)
                game.announce(_(f"{game.player.name} obtained {obj.name}!"))
        game.rooms[y][x] = None
    elif isinstance(room, BaseEvent):
        room.trigger(game, output_func=game.queue_message)
        game.rooms[y][x] = None
    elif isinstance(room, Enemy):
        battle(game, room)
        if not room.is_alive():
            game.rooms[y][x] = None
    elif isinstance(room, EscortNPC):
        game.queue_message(_(f"You find {room.name} who needs escort."))
        room.following = True
        game.rooms[y][x] = None
        game.room_names[y][x] = name
    elif isinstance(room, Companion):
        game.queue_message(_(f"You meet {room.name}. {room.description}"))
        recruit = input(_("Recruit this companion? (y/n): "))
        if recruit.lower() == "y":
            game.player.companions.append(room)
            if room.effect == "attack":
                game.player.attack_power += 2
            elif room.effect == "heal":
                game.player.max_health += 5
                game.player.health += 5
            game.announce(_(f"{game.player.name} gains a companion!"))
        game.rooms[y][x] = None
    elif isinstance(room, Item):
        game.queue_message(_(f"You found a {room.name}!"))
        game.player.collect_item(room)
        game.announce(_(f"{game.player.name} obtained {room.name}!"))
        game.rooms[y][x] = None
        if room.name == "Key":
            game.room_names[y][x] = "Hidden Niche"
    elif room == "Treasure":
        gold = random.randint(20, 50)
        game.player.gold += gold
        game.queue_message(_(f"You found a treasure chest with {gold} gold!"))
        if random.random() < 0.3:
            loot = random.choice(game.rare_loot)
            game.queue_message(_(f"Inside you also discover {loot.name}!"))
            game.player.collect_item(loot)
            game.announce(_(f"{game.player.name} picks up {loot.name}!"))
        game.rooms[y][x] = None
        game.room_names[y][x] = "Glittering Vault"
    elif room == "Enchantment":
        game.queue_message(_("You enter a glowing chamber with ancient runes etched in the stone."))
        if game.player.weapon:
            game.queue_message(_(f"Your current weapon is: {game.player.weapon.name}"))
            game.queue_message(_("You may enchant it with a status effect for 30 gold."))
            game.queue_message(_("1. Poison  2. Burn  3. Freeze  4. Cancel"))
            choice = input(_("Choose enchantment: "))
            if game.player.weapon.effect:
                game.queue_message(
                    _("Your weapon is already enchanted! You can't add another enchantment.")
                )
            elif game.player.gold >= 30 and choice in ["1", "2", "3"]:
                effect = {"1": "poison", "2": "burn", "3": "freeze"}[choice]
                game.player.weapon.description += f" (Enchanted: {effect})"
                game.player.weapon.effect = effect
                game.player.gold -= 30
                game.queue_message(_(f"Your weapon is now enchanted with {effect}!"))
            elif choice == "4":
                game.queue_message(_("You leave the enchantment chamber untouched."))
            else:
                game.queue_message(_("Not enough gold or invalid choice."))
        else:
            game.queue_message(_("You need a weapon to enchant."))
        game.rooms[y][x] = None
        game.room_names[y][x] = "Enchantment Chamber"
    elif room == "Blacksmith":
        game.queue_message(_("You meet a grizzled blacksmith hammering at a forge."))
        if game.player.weapon:
            game.queue_message(
                _(
                    f"Your weapon: {game.player.weapon.name} ({game.player.weapon.min_damage}-{game.player.weapon.max_damage})"
                )
            )
            game.queue_message(
                _("Would you like to upgrade your weapon for 50 gold? +3 min/max damage")
            )
            confirm = input(_("Upgrade? (y/n): "))
            if confirm.lower() == "y" and game.player.gold >= 50:
                game.player.weapon.min_damage += 3
                game.player.weapon.max_damage += 3
                game.player.gold -= 50
                game.queue_message(_("Your weapon has been reforged and is stronger!"))
            elif game.player.gold < 50:
                game.queue_message(_("You don't have enough gold."))
            else:
                game.queue_message(_("Maybe next time."))
        else:
            game.queue_message(
                _(
                    "The blacksmith scoffs. 'No weapon? Come back when you have something worth forging.'"
                )
            )
        game.rooms[y][x] = None
        game.room_names[y][x] = "Blacksmith Forge"

    elif room == "Sanctuary":
        game.player.health = game.player.max_health
        game.queue_message(_("A soothing warmth envelops you. Your wounds are fully healed."))
        game.rooms[y][x] = None
        game.room_names[y][x] = "Sacred Sanctuary"

    elif room == "Trap":
        riddle = random.choice(game.riddles)
        game.queue_message(_("A trap springs! Solve this riddle to escape unharmed:"))
        game.queue_message(riddle["question"])
        response = input(_("Answer: ")).strip().lower()
        if response == riddle["answer"].lower():
            game.queue_message(_("The mechanism clicks harmlessly. You solved it!"))
            game.announce(_("Brilliant puzzle solving!"))
        else:
            damage = random.randint(10, 30)
            game.player.take_damage(damage, source="The Trap")
            game.queue_message(_(f"Wrong answer! You take {damage} damage."))
        game.rooms[y][x] = None
        game.room_names[y][x] = "Booby-Trapped Passage"
    elif room == "Exit":
        game.room_names[y][x] = "Sealed Gate"
        if not game.stairs_prompt_shown:
            game.queue_message(_("Tip: [R]un to descend the stairs quickly."))
            game.stairs_prompt_shown = True
        if game.player.has_item("Key"):
            game.queue_message(_("🎉 You unlocked the exit and escaped the dungeon!"))
            game.queue_message(_(f"Final Score: {game.player.get_score()}"))
            exit()
        else:
            game.queue_message(_("The exit is locked. You need a key!"))

    game.rooms[game.player.y][game.player.x] = None
    game.player.x, game.player.y = x, y
    game.rooms[y][x] = game.player
    game.visited_rooms.add((x, y))
    game.audience_gift()
    game.check_quest_progress()
