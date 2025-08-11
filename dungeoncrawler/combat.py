"""Combat related functionality for the dungeon crawler game."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .dungeon import DungeonBase
    from .entities import Enemy


def battle(game: "DungeonBase", enemy: "Enemy") -> None:
    """Run a battle between the player and ``enemy``.

    Parameters
    ----------
    game:
        The active :class:`~dungeoncrawler.dungeon.DungeonBase` instance.
    enemy:
        The enemy the player is fighting.
    """

    player = game.player
    print(
        f"You encountered a {enemy.name}! {enemy.ability.capitalize() if enemy.ability else ''} Boss incoming!"
    )
    game.announce(f"{player.name} engages {enemy.name}!")
    while player.is_alive() and enemy.is_alive():
        skip_player = player.apply_status_effects()
        for companion in getattr(player, "companions", []):
            companion.assist(player, enemy)
        if not enemy.is_alive():
            break
        if skip_player:
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.take_turn(player)
            continue

        print(f"Player Health: {player.health}")
        print(f"Enemy Health: {enemy.health}")
        print("1. Attack\n2. Defend\n3. Use Health Potion\n4. Use Skill")
        choice = input("Choose action: ")
        if choice == "1":
            player.attack(enemy)
            game.announce("A fierce attack lands!")
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.take_turn(player)
        elif choice == "2":
            player.defend(enemy)
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.take_turn(player)
        elif choice == "3":
            player.use_health_potion()
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.take_turn(player)
        elif choice == "4":
            player.use_skill(enemy)
            game.announce("Special skill unleashed!")
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.take_turn(player)
        else:
            print("Invalid choice!")
        player.decrement_cooldowns()

    if not enemy.is_alive():
        game.announce(f"{enemy.name} has been defeated!")
        if enemy.name in game.boss_loot:
            loot = random.choice(game.boss_loot[enemy.name])
            player.collect_item(loot)
            print(f"The {enemy.name} dropped {loot.name}!")
            game.announce(f"{player.name} obtains {loot.name}!")

