"""Combat related functionality for the dungeon crawler game."""

from __future__ import annotations

import random
from gettext import gettext as _
from typing import TYPE_CHECKING

from .constants import INVALID_KEY_MSG
from .core.combat import resolve_enemy_turn, resolve_player_action
from .core.entity import Entity as CoreEntity
from .input import keys
from .status_effects import format_status_tags
from .ui.terminal import Renderer

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .dungeon import DungeonBase
    from .entities import Enemy, Player


def enemy_turn(enemy: "Enemy", player: "Player", renderer: Renderer | None = None) -> None:
    """Handle the enemy's turn by applying status effects and attacking.

    Parameters
    ----------
    enemy:
        The active enemy in battle.
    player:
        The player being targeted.
    """

    if enemy.is_alive():
        renderer = renderer or Renderer()
        skip = enemy.apply_status_effects()
        if enemy.is_alive() and not skip:
            enemy_entity = CoreEntity(
                enemy.name,
                {"health": enemy.health, "attack": getattr(enemy, "attack_power", 0), "speed": getattr(enemy, "speed", 0)},
            )
            player_entity = CoreEntity(
                player.name,
                {"health": player.health, "defense": 0, "speed": getattr(player, "speed", 0)},
            )
            events = resolve_enemy_turn(enemy_entity, player_entity)
            enemy.health = enemy_entity.stats["health"]
            player.health = player_entity.stats["health"]
            renderer.render_events(events)
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
    renderer = getattr(game, "renderer", Renderer())
    game.stats_logger.battle_start()
    renderer.show_message(
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
            enemy_turn(enemy, player, renderer)
            continue

        renderer.show_message(
            _(f"Player Health: {player.health} {format_status_tags(player.status_effects)}")
        )
        renderer.show_message(
            _(f"Enemy Health: {enemy.health} {format_status_tags(enemy.status_effects)}")
        )
        if enemy.intent_message:
            renderer.show_message(_(enemy.intent_message))
        renderer.show_message(_(f"Stamina: {player.stamina}/{player.max_stamina}"))
        renderer.show_message(_("1. Attack\n2. Defend\n3. Use Health Potion\n4. Use Skill\n5. Flee"))
        key = keys.read_key(_("Choose action: "))
        action = keys.get_action(key)
        combat_action = {
            keys.Action.MOVE_LEFT: "attack",
            keys.Action.MOVE_RIGHT: "defend",
            keys.Action.MOVE_UP: "potion",
            keys.Action.MOVE_DOWN: "skill",
            keys.Action.VISIT_SHOP: "flee",
        }.get(action)
        if combat_action == "attack":
            p_entity = CoreEntity(
                player.name,
                {
                    "health": player.health,
                    "attack": getattr(player, "attack_power", 0),
                    "max_health": player.max_health,
                    "speed": getattr(player, "speed", 0),
                },
            )
            e_entity = CoreEntity(
                enemy.name,
                {
                    "health": enemy.health,
                    "attack": getattr(enemy, "attack_power", 0),
                    "max_health": enemy.max_health,
                    "speed": getattr(enemy, "speed", 0),
                },
            )
            events = resolve_player_action(p_entity, e_entity, "attack")
            player.health = p_entity.stats["health"]
            enemy.health = e_entity.stats["health"]
            renderer.render_events(events)
            game.announce(_("A fierce attack lands!"))
            enemy_turn(enemy, player, renderer)
        elif combat_action == "defend":
            p_entity = CoreEntity(
                player.name,
                {
                    "health": player.health,
                    "attack": getattr(player, "attack_power", 0),
                    "max_health": player.max_health,
                    "speed": getattr(player, "speed", 0),
                },
            )
            e_entity = CoreEntity(
                enemy.name,
                {
                    "health": enemy.health,
                    "attack": getattr(enemy, "attack_power", 0),
                    "max_health": enemy.max_health,
                    "speed": getattr(enemy, "speed", 0),
                },
            )
            events = resolve_player_action(p_entity, e_entity, "defend")
            player.health = p_entity.stats["health"]
            enemy.health = e_entity.stats["health"]
            renderer.render_events(events)
            enemy_turn(enemy, player, renderer)
        elif combat_action == "potion":
            player.use_health_potion()
            enemy_turn(enemy, player, renderer)
        elif combat_action == "skill":
            player.use_skill(enemy)
            game.announce(_("Special skill unleashed!"))
            enemy_turn(enemy, player, renderer)
        elif combat_action == "flee":
            p_entity = CoreEntity(
                player.name,
                {
                    "health": player.health,
                    "attack": getattr(player, "attack_power", 0),
                    "max_health": player.max_health,
                    "speed": getattr(player, "speed", 0),
                },
            )
            e_entity = CoreEntity(
                enemy.name,
                {
                    "health": enemy.health,
                    "attack": getattr(enemy, "attack_power", 0),
                    "max_health": enemy.max_health,
                    "speed": getattr(enemy, "speed", 0),
                },
            )
            events = resolve_player_action(p_entity, e_entity, "flee")
            renderer.render_events(events)
            if events[-1].data.get("success"):
                game.announce(f"{player.name} flees from {enemy.name}!")
                break
            enemy_turn(enemy, player, renderer)
        else:
            renderer.show_message(_(INVALID_KEY_MSG))
        player.decrement_cooldowns()

    if not enemy.is_alive():
        game.announce(f"{enemy.name} has been defeated!")
        if enemy.name in game.boss_loot:
            loot = random.choice(game.boss_loot[enemy.name])
            player.collect_item(loot)
            renderer.show_message(_(f"The {enemy.name} dropped {loot.name}!"))
            game.announce(_(f"{player.name} obtains {loot.name}!"))
    game.stats_logger.battle_end(player.is_alive(), enemy.name)
    game.check_quest_progress()
