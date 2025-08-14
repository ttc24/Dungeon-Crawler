import csv
import time
from pathlib import Path
from typing import Dict, List, Optional


class StatsLogger:
    """Collect and persist balance metrics for each dungeon run."""

    def __init__(self) -> None:
        self.run_id = int(time.time())
        self.rows: List[Dict[str, object]] = []
        self.combat_rows: List[Dict[str, object]] = []
        self.current_floor: Optional[int] = None
        self.turns = 0
        self.encounters = 0
        self.first_reward_turn: Optional[int] = None
        self.total_tiles = 0
        # per-battle trackers
        self._battle_enemy: Optional[str] = None
        self._battle_turns = 0
        self._damage_dealt = 0
        self._damage_taken = 0
        self._skills_used: List[str] = []

    def start_floor(self, game, floor: int) -> None:
        """Begin tracking stats for ``floor``."""
        self.current_floor = floor
        self.turns = 0
        self.encounters = 0
        self.first_reward_turn = None
        self.total_tiles = game.width * game.height

    def record_move(self) -> None:
        self.turns += 1

    # ------------------------------------------------------------------
    # Combat logging helpers
    # ------------------------------------------------------------------
    def battle_start(self, enemy: str) -> None:
        """Begin tracking a combat encounter."""
        self.encounters += 1
        self._battle_enemy = enemy
        self._battle_turns = 0
        self._damage_dealt = 0
        self._damage_taken = 0
        self._skills_used = []

    def record_turn(self) -> None:
        self._battle_turns += 1

    def record_damage(self, *, dealt: int = 0, taken: int = 0) -> None:
        self._damage_dealt += max(0, dealt)
        self._damage_taken += max(0, taken)

    def record_skill(self, name: str) -> None:
        self._skills_used.append(name)

    def battle_end(self, victory: bool, enemy: str) -> None:
        """Persist collected combat stats for the current battle."""
        if self._battle_enemy is None:
            self._battle_enemy = enemy
        self.combat_rows.append(
            {
                "run_id": self.run_id,
                "floor": self.current_floor if self.current_floor is not None else "",
                "enemy": self._battle_enemy,
                "turns": self._battle_turns,
                "damage_dealt": self._damage_dealt,
                "damage_taken": self._damage_taken,
                "skills_used": ";".join(self._skills_used),
                "win": int(bool(victory)),
            }
        )
        self._battle_enemy = None

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
        """Write collected metrics to ``logs`` directory."""
        if self.current_floor is not None:
            self.end_floor(game)
        path = Path("logs")
        path.mkdir(parents=True, exist_ok=True)

        if self.rows:
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

        if self.combat_rows:
            csv_path = path / "combat.csv"
            fieldnames = [
                "run_id",
                "floor",
                "enemy",
                "turns",
                "damage_dealt",
                "damage_taken",
                "skills_used",
                "win",
            ]
            file_exists = csv_path.exists()
            with csv_path.open("a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                for row in self.combat_rows:
                    writer.writerow(row)
            self.combat_rows.clear()
