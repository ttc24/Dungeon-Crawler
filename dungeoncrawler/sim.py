"""Automated combat simulation utilities."""

from __future__ import annotations

import argparse
import random
from typing import Dict, Mapping

from .core.combat import resolve_enemy_turn, resolve_player_action
from .core.entity import Entity
from .dungeon import ENEMY_STATS


def simulate_battles(
    enemy_name: str,
    runs: int,
    seed: int | None = None,
    player_stats: Mapping[str, int] | None = None,
) -> Dict[str, float]:
    """Simulate ``runs`` battles against ``enemy_name``.

    Parameters
    ----------
    enemy_name:
        Name of the enemy archetype to fight.
    runs:
        Number of battles to simulate.
    seed:
        Optional seed for deterministic results.
    player_stats:
        Optional mapping defining the player's ``health``, ``attack`` and
        ``speed`` values. Defaults to a basic hero profile.

    Returns
    -------
    dict
        Dictionary with ``winrate`` and ``avg_turns``.
    """

    rng = random.Random(seed)
    if enemy_name not in ENEMY_STATS:
        raise KeyError(f"Unknown enemy: {enemy_name}")
    hp_min, hp_max, atk_min, atk_max, defense = ENEMY_STATS[enemy_name]
    wins = 0
    total_turns = 0
    base_player = {"health": 30, "attack": 8, "speed": 10}
    if player_stats:
        base_player.update(player_stats)
    for _ in range(runs):
        player = Entity("Hero", base_player.copy())
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


def main() -> None:
    """Command line entry point for quick balance simulations."""

    parser = argparse.ArgumentParser(description="Simulate battles against a given enemy.")
    parser.add_argument("enemy", help="Enemy name to fight")
    parser.add_argument("--runs", type=int, default=100, help="Number of battles to simulate")
    parser.add_argument(
        "--seed", type=int, default=None, help="Optional seed for deterministic results"
    )
    parser.add_argument("--player-health", type=int, default=30, help="Player health value")
    parser.add_argument("--player-attack", type=int, default=8, help="Player attack value")
    parser.add_argument("--player-speed", type=int, default=10, help="Player speed value")
    args = parser.parse_args()

    player_stats = {
        "health": args.player_health,
        "attack": args.player_attack,
        "speed": args.player_speed,
    }

    stats = simulate_battles(args.enemy, args.runs, seed=args.seed, player_stats=player_stats)
    print(f"Winrate: {stats['winrate']:.2%}")
    print(f"Average Turns: {stats['avg_turns']:.2f}")


if __name__ == "__main__":
    main()
