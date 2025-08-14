"""Deterministic combat resolution helpers.

The functions defined here operate on :class:`~dungeoncrawler.core.entity.Entity`
instances and return typed event objects describing the outcome of an action.
No printing or random number generation occurs which makes the module suitable
for unit testing and simulations.
"""

from __future__ import annotations

from typing import List

from .data import load_items
from .entity import Entity
from .events import AttackResolved, Event, IntentTelegraphed, StatusApplied


def calculate_hit(attacker: Entity, defender: Entity) -> int:
    """Return the attacker's hit chance against ``defender``.

    A base 75% chance is modified by the speed difference between
    ``attacker`` and ``defender``.  Temporary status flags may further
    modify the result:

    * ``advantage`` – grants +15% hit and is consumed.
    * ``defend_attack`` – grants +10% hit and is consumed.

    The value is clamped between 0 and 100.
    """

    hit = 75 + attacker.stats.get("speed", 0) - defender.stats.get("speed", 0)
    if "advantage" in attacker.status:
        hit += 15
        attacker.status.remove("advantage")
    if "defend_attack" in attacker.status:
        hit += 10
        attacker.status.remove("defend_attack")
    return max(0, min(100, hit))


def calculate_crit(attacker: Entity, defender: Entity) -> int:
    """Return the attacker's critical hit chance.

    Uses the attacker's ``crit`` stat reduced by the defender's
    ``tenacity`` stat if present.  The result is clamped between
    0 and 100.
    """

    crit = attacker.stats.get("crit", 0) - defender.stats.get("tenacity", 0)
    return max(0, min(100, crit))


def calculate_damage(attacker: Entity, defender: Entity, critical: bool = False) -> int:
    """Compute damage dealt from ``attacker`` to ``defender``.

    The basic formula is ``attack - defense``.  If ``critical`` is ``True``
    the damage is doubled.  If the defender has the temporary status
    ``defend_damage`` incoming damage is reduced by 40% and the status is
    consumed.
    """

    attack = attacker.stats.get("attack", 0)
    defense = defender.stats.get("defense", 0)
    damage = max(0, attack - defense)
    if critical:
        damage *= 2
    if "defend_damage" in defender.status:
        damage = int(damage * 0.6)
        defender.status.remove("defend_damage")
    defender.stats["health"] = max(0, defender.stats.get("health", 0) - damage)
    return damage


# ---------------------------------------------------------------------------
# Core resolvers
# ---------------------------------------------------------------------------


def resolve_attack(attacker: Entity, defender: Entity) -> AttackResolved:
    """Resolve a basic attack from ``attacker`` to ``defender``."""

    hit = calculate_hit(attacker, defender)
    if hit < 50:
        msg = f"{attacker.name} misses {defender.name}."
        return AttackResolved(msg, attacker.name, defender.name, 0, 0)

    crit_chance = calculate_crit(attacker, defender)
    critical = crit_chance >= 100
    damage = calculate_damage(attacker, defender, critical)
    defeated = int(not defender.is_alive())
    if critical:
        msg = f"{attacker.name} critically hits {defender.name} for {damage} damage."
    else:
        msg = f"{attacker.name} hits {defender.name} for {damage} damage."
    if defeated:
        msg += f" {defender.name} is defeated."
    return AttackResolved(msg, attacker.name, defender.name, damage, defeated)


def resolve_player_action(player: Entity, enemy: Entity, action: str) -> List[Event]:
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

    events: List[Event] = []
    if action == "attack":
        events.append(resolve_attack(player, enemy))
    elif action == "defend":
        player.status.extend(["defend_damage", "defend_attack"])
        events.append(StatusApplied(f"{player.name} defends.", player.name, "defend", 1))
    elif action == "use_health_potion":
        if "potion" in player.inventory:
            player.inventory.remove("potion")
            potion = load_items().get("potion", {})
            heal = player.stats.get("potion_heal", potion.get("potion_heal", 20))
            max_hp = player.stats.get("max_health", player.stats.get("health", 0))
            new_hp = min(max_hp, player.stats.get("health", 0) + heal)
            player.stats["health"] = new_hp
            events.append(
                StatusApplied(
                    f"{player.name} uses a health potion and heals {heal} health.",
                    player.name,
                    "healed",
                    0,
                    value=heal,
                )
            )
        else:
            events.append(
                StatusApplied(f"{player.name} has no potion.", player.name, "heal_failed", 0)
            )
    elif action == "flee":
        speed_diff = player.stats.get("speed", 0) - enemy.stats.get("speed", 0)
        chance = max(10, min(90, 40 + speed_diff * 5))
        success = int(chance > 50)
        if success:
            msg = f"{player.name} flees from {enemy.name}."
        else:
            msg = f"{player.name} fails to flee from {enemy.name}."
            enemy.status.append("advantage")
        events.append(StatusApplied(msg, player.name, "flee", 0, value=success))
    else:
        events.append(StatusApplied("Unknown action.", player.name, "unknown", 0))
    return events


def resolve_enemy_turn(enemy: Entity, player: Entity) -> List[Event]:
    """Resolve the enemy's turn against ``player``.

    The enemy first telegraphs its intent then performs the action. If no intent
    generator is provided the enemy defaults to a basic attack.
    """

    if not enemy.is_alive():
        return [
            StatusApplied(f"{enemy.name} is defeated and cannot act.", enemy.name, "defeated", 0)
        ]

    events: List[Event] = []

    action = "attack"
    message = f"{enemy.name} attacks."
    if enemy.intent is not None:
        try:
            action, message = next(enemy.intent)
        except StopIteration:
            pass

    events.append(IntentTelegraphed(message, enemy.name, action))

    if action == "attack":
        events.append(resolve_attack(enemy, player))
    elif action == "defend":
        enemy.status.extend(["defend_damage", "defend_attack"])
        events.append(StatusApplied(f"{enemy.name} defends.", enemy.name, "defend", 1))
    else:
        events.append(resolve_attack(enemy, player))

    return events
