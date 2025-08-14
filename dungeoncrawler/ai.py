import json
import random
from pathlib import Path


class AggressiveAI:
    """Simple AI that always chooses to attack."""

    def choose_action(self, enemy, player):
        return "attack"


class DefensiveAI:
    """AI that prioritizes defense when health is low."""

    def choose_action(self, enemy, player):
        if enemy.health <= enemy.max_health // 2 and "shield" not in enemy.status_effects:
            return "defend"
        return "attack"


class IntentAI:
    """Weighted three-state controller for enemy behaviour.

    Each enemy configured with this AI chooses between Aggressive,
    Defensive and Unpredictable intents every turn according to the
    provided weights.  The chosen intent is *telegraphed* to the player in
    advance so they can react during their turn.

    Parameters
    ----------
    aggressive: int
        Relative weight for selecting an aggressive action.
    defensive: int
        Relative weight for selecting a defensive action.
    unpredictable: int
        Relative weight for selecting an unpredictable action.
    """

    TELEGRAPHS = {
        "Goblin": {
            "aggressive": "Goblin winds up a heavy strike…",
            "defensive": "Goblin raises its guard.",
            "unpredictable": "The Goblin grins wildly, unpredictable…",
        },
        "Beetle": {
            "defensive": "Beetle curls into its shell.",
        },
        "Acolyte": {
            "aggressive": "Acolyte begins channeling (interrupt with 8+ damage).",
        },
    }

    def __init__(self, aggressive=1, defensive=1, unpredictable=1):
        self.weights = {
            "aggressive": aggressive,
            "defensive": defensive,
            "unpredictable": unpredictable,
        }

    # ------------------------------------------------------------------
    def choose_intent(self, enemy, player):
        """Select the next action and telegraph it to the player.

        Returns
        -------
        tuple[str, str]
            A pair ``(action, message)`` describing what the enemy will do on
            its next turn and the text used to foreshadow that intent.
        """

        intents = list(self.weights.keys())
        weights = list(self.weights.values())
        intent = random.choices(intents, weights=weights, k=1)[0]

        # Map intents to actions and default telegraphs
        action = "attack"
        message = {
            "aggressive": f"The {enemy.name} winds up for a heavy strike…",
            "defensive": f"The {enemy.name} raises its guard.",
            "unpredictable": f"The {enemy.name} wavers unpredictably…",
        }[intent]

        if intent == "aggressive" and getattr(enemy, "heavy_cd", 0) == 0:
            action = "heavy_attack"
        elif intent == "defensive" and enemy.health <= enemy.max_health // 3:
            action = "defend"
        elif intent == "unpredictable":
            action = random.choice(["wild_attack", "defend"])

        # Custom telegraphs for specific enemy archetypes
        telegraphs = self.TELEGRAPHS.get(enemy.name, {})
        message = telegraphs.get(intent, message)

        return action, message

    # Backwards compatibility for older saves/tests
    plan_next = choose_intent


# Extend telegraphs for enemies defined in floors.json
try:
    _floors_path = Path(__file__).resolve().parents[1] / "data" / "floors.json"
    with _floors_path.open() as _f:
        _floors = json.load(_f)
    for _cfg in _floors.values():
        for _name in _cfg.get("enemies", []):
            IntentAI.TELEGRAPHS.setdefault(
                _name,
                {
                    "aggressive": f"{_name} prepares a vicious strike.",
                    "defensive": f"{_name} braces for incoming attacks.",
                    "unpredictable": f"{_name} shifts unpredictably.",
                },
            )
except FileNotFoundError:
    pass


# Default archetype weights for enemies that use IntentAI
ARCHETYPES = {
    "Goblin": {"aggressive": 3, "defensive": 1, "unpredictable": 1},
    "Beetle": {"aggressive": 1, "defensive": 3, "unpredictable": 1},
    "Acolyte": {"aggressive": 2, "defensive": 1, "unpredictable": 2},
}
