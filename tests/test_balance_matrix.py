import pytest
import yaml

from dungeoncrawler.sim import simulate

with open("balance_thresholds.yml") as f:
    CONFIG = yaml.safe_load(f)


@pytest.mark.balance
@pytest.mark.parametrize("case", CONFIG["matchups"])
def test_balance_matrix(case):
    result = simulate(
        case["player_class"],
        case["enemy_kind"],
        case["floor"],
        case.get("runs", 100),
    )
    assert case["min"] <= result.win_rate <= case["max"]
