"""Combat helpers for the dungeon crawler game."""

from __future__ import annotations

import random

from .map import BOSS_LOOT


def battle(game, enemy):
    """Run a battle between ``game.player`` and ``enemy``."""

    print(
        f"You encountered a {enemy.name}! {enemy.ability.capitalize() if enemy.ability else ''}"
        " Boss incoming!"
    )
    game.announce(f"{game.player.name} engages {enemy.name}!")
    while game.player.is_alive() and enemy.is_alive():
        game.player.apply_status_effects()
        for companion in getattr(game.player, "companions", []):
            companion.assist(game.player, enemy)
        if not enemy.is_alive():
            break
        if "freeze" in game.player.status_effects:
            print("\u2744\ufe0f You are frozen and skip this turn!")
            game.player.status_effects["freeze"] -= 1
            if game.player.status_effects["freeze"] <= 0:
                del game.player.status_effects["freeze"]
            if enemy.is_alive():
                enemy.attack(game.player)
            continue

        print(f"Player Health: {game.player.health}")
        print(f"Enemy Health: {enemy.health}")
        print("1. Attack\n2. Defend\n3. Use Health Potion\n4. Use Skill")
        choice = input("Choose action: ")
        if choice == "1":
            game.player.attack(enemy)
            game.announce("A fierce attack lands!")
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.attack(game.player)
        elif choice == "2":
            game.player.defend(enemy)
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.attack(game.player)
        elif choice == "3":
            game.player.use_health_potion()
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.attack(game.player)
        elif choice == "4":
            game.player.use_skill(enemy)
            game.announce("Special skill unleashed!")
            if enemy.is_alive():
                skip = enemy.apply_status_effects()
                if enemy.is_alive() and not skip:
                    enemy.attack(game.player)
        else:
            print("Invalid choice!")
        game.player.decrement_cooldowns()

    if not enemy.is_alive():
        game.announce(f"{enemy.name} has been defeated!")
        if enemy.name in BOSS_LOOT:
            loot = random.choice(BOSS_LOOT[enemy.name])
            game.player.collect_item(loot)
            print(f"The {enemy.name} dropped {loot.name}!")
            game.announce(f"{game.player.name} obtains {loot.name}!")

