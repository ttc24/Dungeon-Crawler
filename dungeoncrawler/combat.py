"""Combat related functionality for the dungeon crawler game."""

from __future__ import annotations

from gettext import gettext as _
from typing import TYPE_CHECKING

from .constants import INVALID_KEY_MSG
from .core.combat import resolve_enemy_turn, resolve_player_action
from .core.entity import Entity as CoreEntity
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

    renderer = renderer or Renderer()
    if enemy.is_alive():
        skip = enemy.apply_status_effects()
        if enemy.is_alive() and not skip:
            enemy_entity = CoreEntity(
                enemy.name,
                {
                    "health": enemy.health,
                    "attack": getattr(enemy, "attack_power", 0),
                    "speed": getattr(enemy, "speed", 0),
                },
            )
            # Use the preselected intent so the telegraphed action is executed.
            enemy_entity.intent = (item for item in [(enemy.next_action, enemy.intent_message)])
            player_entity = CoreEntity(
                player.name,
                {"health": player.health, "defense": 0, "speed": getattr(player, "speed", 0)},
            )
            events = resolve_enemy_turn(enemy_entity, player_entity)
            enemy.health = enemy_entity.stats["health"]
            player.health = player_entity.stats["health"]
            for event in events:
                renderer.handle_event(event)
        if enemy.heavy_cd > 0:
            enemy.heavy_cd -= 1


def battle(game: "DungeonBase", enemy: "Enemy", input_func=None) -> None:
    """Run a battle between the player and ``enemy``.

    Parameters
    ----------
    game:
        The active :class:`~dungeoncrawler.dungeon.DungeonBase` instance.
    enemy:
        The enemy the player is fighting.
    """

    if input_func is None:
        input_func = input
    player = game.player
    game.stats_logger.battle_start(enemy.name)
    renderer = getattr(game, "renderer", Renderer())
    renderer.show_message(
        _(
            f"You encountered a {enemy.name}! {enemy.ability.capitalize() if enemy.ability else ''} Boss incoming!"
        )
    )
    game.announce(f"{player.name} engages {enemy.name}!")
    while player.is_alive() and enemy.is_alive():
        skip_player = player.apply_status_effects()
        for companion in getattr(player, "companions", []):
            companion.assist(player, enemy)
        if not enemy.is_alive():
            break
        if enemy.ai and hasattr(enemy.ai, "choose_intent"):
            enemy.next_action, enemy.intent, enemy.intent_message = enemy.ai.choose_intent(
                enemy, player
            )
        else:
            enemy.next_action = None
            enemy.intent = None
            enemy.intent_message = ""
        if skip_player:
            before = player.health
            enemy_turn(enemy, player, renderer)
            game.stats_logger.record_damage(taken=before - player.health)
            game.stats_logger.record_turn()
            continue

        renderer.show_message(
            _(f"Player Health: {player.health} {format_status_tags(player.status_effects)}")
        )
        renderer.show_message(
            _(f"Enemy Health: {enemy.health} {format_status_tags(enemy.status_effects)}")
        )
        if enemy.intent:
            renderer.show_message(_(f"Intent: {enemy.intent}"))
        if enemy.intent_message:
            renderer.show_message(_(enemy.intent_message))
        renderer.show_message(_(f"Stamina: {player.stamina}/{player.max_stamina}"))
        renderer.show_message(
            _("1. Attack\n2. Defend\n3. Use Health Potion\n4. Use Skill\n5. Flee")
        )
        choice = input_func(_("Choose action: "))
        if choice == "1":
            enemy_before = enemy.health
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
            for event in events:
                renderer.handle_event(event)
            game.announce(_("A fierce attack lands!"))
            game.stats_logger.record_damage(dealt=enemy_before - enemy.health)
            before = player.health
            enemy_turn(enemy, player, renderer)
            game.stats_logger.record_damage(taken=before - player.health)
            game.stats_logger.record_turn()
        elif choice == "2":
            enemy_before = enemy.health
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
            for event in events:
                renderer.handle_event(event)
            game.stats_logger.record_damage(dealt=enemy_before - enemy.health)
            before = player.health
            enemy_turn(enemy, player, renderer)
            game.stats_logger.record_damage(taken=before - player.health)
            game.stats_logger.record_turn()
        elif choice == "3":
            player.use_health_potion()
            before = player.health
            enemy_turn(enemy, player, renderer)
            game.stats_logger.record_damage(taken=before - player.health)
            game.stats_logger.record_turn()
        elif choice == "4":
            enemy_before = enemy.health
            skill_name = player.use_skill(enemy)
            if skill_name:
                game.stats_logger.record_skill(skill_name)
            game.announce(_("Special skill unleashed!"))
            game.stats_logger.record_damage(dealt=enemy_before - enemy.health)
            before = player.health
            enemy_turn(enemy, player, renderer)
            game.stats_logger.record_damage(taken=before - player.health)
            game.stats_logger.record_turn()
        elif choice == "5":
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
            for event in events:
                renderer.handle_event(event)
            if events[-1].data.get("success"):
                game.announce(f"{player.name} flees from {enemy.name}!")
                game.stats_logger.record_turn()
                break
            before = player.health
            enemy_turn(enemy, player, renderer)
            game.stats_logger.record_damage(taken=before - player.health)
            game.stats_logger.record_turn()
        else:
            renderer.show_message(_(INVALID_KEY_MSG))
        player.decrement_cooldowns()

    if not enemy.is_alive():
        game.announce(f"{enemy.name} has been defeated!")
        if enemy.name in game.boss_loot:
            for loot in game.boss_loot[enemy.name]:
                player.collect_item(loot)
                renderer.show_message(_(f"The {enemy.name} dropped {loot.name}!"))
                game.announce(_(f"{player.name} obtains {loot.name}!"))
    game.stats_logger.battle_end(player.is_alive(), enemy.name)
    game.check_quest_progress()
