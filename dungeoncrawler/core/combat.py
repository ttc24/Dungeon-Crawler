"""Deterministic combat resolution helpers.

The functions defined here operate on :class:`~dungeoncrawler.core.entity.Entity`
instances and return lightweight event objects describing the outcome of an
action.  No printing or random number generation occurs which makes the module
suitable for unit testing and simulations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .entity import Entity


@dataclass
class CombatEvent:
    """Container describing the result of a combat action."""

    type: str
    message: str
    data: Dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Core resolvers
# ---------------------------------------------------------------------------

def resolve_attack(attacker: Entity, defender: Entity) -> CombatEvent:
    """Resolve a basic attack from ``attacker`` to ``defender``.

    Damage is computed deterministically from the ``attack`` and ``defense``
    stats. The defender's ``health`` stat is reduced in-place.  The returned
    :class:`CombatEvent` contains the amount of damage dealt and whether the
    defender was defeated.
    """

    attack = attacker.stats.get("attack", 0)
    defense = defender.stats.get("defense", 0)
    damage = max(0, attack - defense)
    defender.stats["health"] = max(0, defender.stats.get("health", 0) - damage)
    defeated = int(not defender.is_alive())
    msg = f"{attacker.name} hits {defender.name} for {damage} damage."
    if defeated:
        msg += f" {defender.name} is defeated."
    return CombatEvent("attack", msg, {"damage": damage, "defeated": defeated})


def resolve_player_action(player: Entity, enemy: Entity, action: str) -> List[CombatEvent]:
    """Resolve a player's ``action`` against ``enemy``.

    Parameters
    ----------
    player:
        Acting entity.
    enemy:
        Target entity.
    action:
        Action keyword. Supported values are ``"attack"``, ``"defend"``,
        ``"use_health_potion"`` and ``"flee"``.
    """

    events: List[CombatEvent] = []
    if action == "attack":
        events.append(resolve_attack(player, enemy))
    elif action == "defend":
        player.status.append("defending")
        events.append(CombatEvent("defend", f"{player.name} defends.", {}))
    elif action == "use_health_potion":
        if "potion" in player.inventory:
            player.inventory.remove("potion")
            heal = player.stats.get("potion_heal", 20)
            max_hp = player.stats.get("max_health", player.stats.get("health", 0))
            new_hp = min(max_hp, player.stats.get("health", 0) + heal)
            player.stats["health"] = new_hp
            events.append(
                CombatEvent(
                    "heal", f"{player.name} uses a health potion and heals {heal} health.", {"heal": heal}
                )
            )
        else:
            events.append(CombatEvent("heal_failed", f"{player.name} has no potion.", {}))
    elif action == "flee":
        success = int(player.stats.get("speed", 0) > enemy.stats.get("speed", 0))
        if success:
            msg = f"{player.name} flees from {enemy.name}."
        else:
            msg = f"{player.name} fails to flee from {enemy.name}."
        events.append(CombatEvent("flee", msg, {"success": success}))
    else:
        events.append(CombatEvent("unknown", "Unknown action.", {}))
    return events


def resolve_enemy_turn(enemy: Entity, player: Entity) -> List[CombatEvent]:
    """Resolve the enemy's turn against ``player``.

    Currently this simply performs a basic attack if the enemy is alive.
    """

    if not enemy.is_alive():
        return [CombatEvent("noop", f"{enemy.name} is defeated and cannot act.", {})]
    return [resolve_attack(enemy, player)]
