import csv
import time
from pathlib import Path
from typing import Dict, List, Optional


class StatsLogger:
    """Collect and persist balance metrics for each dungeon run."""

    def __init__(self) -> None:
        self.run_id = int(time.time())
        self.rows: List[Dict[str, object]] = []
        self.current_floor: Optional[int] = None
        self.turns = 0
        self.encounters = 0
        self.first_reward_turn: Optional[int] = None
        self.total_tiles = 0

    def start_floor(self, game, floor: int) -> None:
        """Begin tracking stats for ``floor``."""
        self.current_floor = floor
        self.turns = 0
        self.encounters = 0
        self.first_reward_turn = None
        self.total_tiles = game.width * game.height

    def record_move(self) -> None:
        self.turns += 1

    def battle_start(self) -> None:
        self.encounters += 1

    def battle_end(self, *_args, **_kwargs) -> None:  # pragma: no cover - placeholder
        """Hook for future detailed combat metrics."""
        return

    def record_reward(self) -> None:
        if self.first_reward_turn is None:
            self.first_reward_turn = self.turns

    def end_floor(self, game) -> None:
        if self.current_floor is None:
            return
        discovered = sum(1 for row in game.discovered for cell in row if cell)
        fog_rate = discovered / self.total_tiles if self.total_tiles else 0
        self.rows.append(
            {
                "floor": self.current_floor,
                "turns": self.turns,
                "encounters": self.encounters,
                "time_to_first_reward": (
                    self.first_reward_turn if self.first_reward_turn is not None else ""
                ),
                "fog_reveal_rate": round(fog_rate, 3),
            }
        )
        self.current_floor = None

    def finalize(self, game, death_cause: str) -> None:
        """Write collected metrics to ``logs/balance.csv``."""
        if self.current_floor is not None:
            self.end_floor(game)
        if not self.rows:
            return
        path = Path("logs")
        path.mkdir(parents=True, exist_ok=True)
        csv_path = path / "balance.csv"
        fieldnames = [
            "run_id",
            "death_cause",
            "floor",
            "turns",
            "encounters",
            "time_to_first_reward",
            "fog_reveal_rate",
        ]
        file_exists = csv_path.exists()
        with csv_path.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in self.rows:
                row = row.copy()
                row["run_id"] = self.run_id
                row["death_cause"] = death_cause
                writer.writerow(row)
        self.rows.clear()
