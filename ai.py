class AggressiveAI:
    """Simple AI that always chooses to attack."""

    def choose_action(self, enemy, player):
        return "attack"


class DefensiveAI:
    """AI that prioritizes defense when health is low."""

    def choose_action(self, enemy, player):
        if (
            enemy.health <= enemy.max_health // 2
            and "shield" not in enemy.status_effects
        ):
            return "defend"
        return "attack"
