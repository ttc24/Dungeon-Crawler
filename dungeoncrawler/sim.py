"""Automated combat simulation utilities."""

from __future__ import annotations

import random
from typing import Dict

from .core.combat import resolve_enemy_turn, resolve_player_action
from .core.entity import Entity
from .dungeon import ENEMY_STATS


def simulate_battles(enemy_name: str, runs: int, seed: int | None = None) -> Dict[str, float]:
    """Simulate ``runs`` battles against ``enemy_name``.

    Returns a dictionary with ``winrate`` and ``avg_turns``.
    """

    rng = random.Random(seed)
    if enemy_name not in ENEMY_STATS:
        raise KeyError(f"Unknown enemy: {enemy_name}")
    hp_min, hp_max, atk_min, atk_max, defense = ENEMY_STATS[enemy_name]
    wins = 0
    total_turns = 0
    for _ in range(runs):
        player = Entity("Hero", {"health": 30, "attack": 8, "speed": 10})
        enemy = Entity(
            enemy_name,
            {
                "health": rng.randint(hp_min, hp_max),
                "attack": rng.randint(atk_min, atk_max),
                "defense": defense,
                "speed": 10,
            },
        )
        turns = 0
        while player.stats["health"] > 0 and enemy.stats["health"] > 0:
            resolve_player_action(player, enemy, "attack")
            if enemy.stats["health"] <= 0:
                turns += 1
                break
            resolve_enemy_turn(enemy, player)
            turns += 1
        if player.stats["health"] > 0:
            wins += 1
            total_turns += turns
    winrate = wins / runs if runs else 0
    avg_turns = total_turns / wins if wins else 0
    return {"winrate": winrate, "avg_turns": avg_turns}
