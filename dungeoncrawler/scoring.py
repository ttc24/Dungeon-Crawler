from __future__ import annotations

"""Utility helpers for computing final run scores.

The scoring system applies a number of configurable bonuses and penalties to
an underlying base score.  ``compute_score_breakdown`` returns a dictionary
containing the contribution of each component and the final total.  A helper
``format_score_breakdown`` converts that dictionary into human readable lines.
"""

from dataclasses import dataclass
from typing import Mapping, Any

from .config import config


@dataclass
class ScoreBreakdown:
    base: int
    retire_bonus: int
    no_death_bonus: int
    death_penalty: int
    total: int
    floors_early: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "base": self.base,
            "retire_bonus": self.retire_bonus,
            "no_death_bonus": self.no_death_bonus,
            "death_penalty": self.death_penalty,
            "total": self.total,
            "floors_early": self.floors_early,
        }


def compute_score_breakdown(state: Mapping[str, Any]) -> dict[str, int]:
    """Compute a final score breakdown for ``state``.

    Parameters
    ----------
    state:
        Mapping with at least ``base`` (base score), ``floor`` (floor reached)
        and ``died`` (truthy if the run ended in death).
    """

    base = int(state.get("base", 0))
    floor = int(state.get("floor", 0))
    died = bool(state.get("died", False))

    cfg = config
    floors_early = max(cfg.retire_floor - floor, 0) if not died and floor < cfg.retire_floor else 0
    retire_bonus = round(base * cfg.retire_bonus_per_floor * floors_early)
    no_death_bonus = round(base * cfg.no_death_bonus) if not died else 0
    death_penalty = round(base * cfg.death_penalty) if died else 0
    total = base + retire_bonus + no_death_bonus - death_penalty

    breakdown = ScoreBreakdown(
        base=base,
        retire_bonus=int(retire_bonus),
        no_death_bonus=int(no_death_bonus),
        death_penalty=int(death_penalty),
        total=int(total),
        floors_early=int(floors_early),
    )
    return breakdown.to_dict()


def format_score_breakdown(breakdown: Mapping[str, int]) -> list[str]:
    """Return a list of human readable score breakdown lines."""

    cfg = config
    floors = breakdown.get("floors_early", 0)
    lines = [
        f"Base score: {breakdown.get('base', 0)}",
        (
            "Early retire bonus: +{bonus} (retired {floors} floors before Floor {rf} @ {pct}%/floor)".format(
                bonus=breakdown.get("retire_bonus", 0),
                floors=floors,
                rf=cfg.retire_floor,
                pct=int(cfg.retire_bonus_per_floor * 100),
            )
        ),
        f"No-death bonus: +{breakdown.get('no_death_bonus', 0)}",
        f"Death penalty: -{breakdown.get('death_penalty', 0)}",
        f"TOTAL: {breakdown.get('total', 0)}",
    ]
    return lines
