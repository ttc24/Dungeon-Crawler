import subprocess
import sys


def test_simulate_battles_cli():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dungeoncrawler.sim",
            "Bandit",
            "--runs",
            "5",
            "--seed",
            "0",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Winrate:" in result.stdout
    assert "Average Turns:" in result.stdout
