"""Combat related functionality for the dungeon crawler game."""

from __future__ import annotations

import random
from gettext import gettext as _
from typing import TYPE_CHECKING

from .constants import INVALID_KEY_MSG
from .status_effects import format_status_tags

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .dungeon import DungeonBase
    from .entities import Enemy, Player


def enemy_turn(enemy: "Enemy", player: "Player") -> None:
    """Handle the enemy's turn by applying status effects and attacking.

    Parameters
    ----------
    enemy:
        The active enemy in battle.
    player:
        The player being targeted.
    """

    if enemy.is_alive():
        skip = enemy.apply_status_effects()
        if enemy.is_alive() and not skip:
            enemy.take_turn(player)
        if enemy.ai and hasattr(enemy.ai, "choose_intent"):
            enemy.next_action, enemy.intent_message = enemy.ai.choose_intent(enemy, player)
        else:
            enemy.next_action = None
            enemy.intent_message = ""
        if enemy.heavy_cd > 0:
            enemy.heavy_cd -= 1


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
    game.stats_logger.battle_start()
    print(
        _(
            f"You encountered a {enemy.name}! {enemy.ability.capitalize() if enemy.ability else ''} Boss incoming!"
        )
    )
    if enemy.ai and hasattr(enemy.ai, "choose_intent"):
        enemy.next_action, enemy.intent_message = enemy.ai.choose_intent(enemy, player)
    game.announce(f"{player.name} engages {enemy.name}!")
    while player.is_alive() and enemy.is_alive():
        skip_player = player.apply_status_effects()
        for companion in getattr(player, "companions", []):
            companion.assist(player, enemy)
        if not enemy.is_alive():
            break
        if skip_player:
            enemy_turn(enemy, player)
            continue

        print(_(f"Player Health: {player.health} {format_status_tags(player.status_effects)}"))
        print(_(f"Enemy Health: {enemy.health} {format_status_tags(enemy.status_effects)}"))
        if enemy.intent_message:
            print(_(enemy.intent_message))
        print(_(f"Stamina: {player.stamina}/{player.max_stamina}"))
        print(_("1. Attack\n2. Defend\n3. Use Health Potion\n4. Use Skill\n5. Flee"))
        choice = input(_("Choose action: "))
        if choice == "1":
            player.attack(enemy)
            game.announce(_("A fierce attack lands!"))
            enemy_turn(enemy, player)
        elif choice == "2":
            player.defend(enemy)
            enemy_turn(enemy, player)
        elif choice == "3":
            player.use_health_potion()
            enemy_turn(enemy, player)
        elif choice == "4":
            player.use_skill(enemy)
            game.announce(_("Special skill unleashed!"))
            enemy_turn(enemy, player)
        elif choice == "5":
            if player.flee(enemy):
                game.announce(f"{player.name} flees from {enemy.name}!")
                break
            enemy_turn(enemy, player)
        else:
            print(_(INVALID_KEY_MSG))
        player.decrement_cooldowns()

    if not enemy.is_alive():
        game.announce(f"{enemy.name} has been defeated!")
        if enemy.name in game.boss_loot:
            loot = random.choice(game.boss_loot[enemy.name])
            player.collect_item(loot)
            print(_(f"The {enemy.name} dropped {loot.name}!"))
            game.announce(_(f"{player.name} obtains {loot.name}!"))
    game.stats_logger.battle_end(player.is_alive(), enemy.name)
    game.check_quest_progress()
