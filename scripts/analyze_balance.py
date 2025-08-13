"""Utility script to summarize balance metrics and death causes."""

from collections import Counter
import csv
from pathlib import Path
import statistics


def main() -> None:
    path = Path("logs/balance.csv")
    if not path.exists():
        print("No balance log found.")
        return
    runs = {}
    turns = []
    encounters = []
    rewards = []
    fog = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_id = row["run_id"]
            runs.setdefault(run_id, row["death_cause"])
            turns.append(int(row["turns"]))
            encounters.append(int(row["encounters"]))
            if row["time_to_first_reward"]:
                rewards.append(int(row["time_to_first_reward"]))
            fog.append(float(row["fog_reveal_rate"]))
    print("Death Causes:")
    for cause, count in Counter(runs.values()).items():
        print(f"  {cause}: {count}")
    print(f"Average Turns per Floor: {statistics.mean(turns):.2f}")
    print(f"Average Encounters per Floor: {statistics.mean(encounters):.2f}")
    if rewards:
        print(f"Average Turns to First Reward: {statistics.mean(rewards):.2f}")
    print(f"Average Fog Reveal Rate: {statistics.mean(fog):.2f}")


if __name__ == "__main__":
    main()
