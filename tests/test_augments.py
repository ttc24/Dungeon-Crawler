from dungeoncrawler.entities import Player
from dungeoncrawler.items import Augment


def test_augment_stacking_rules():
    player = Player("Hero")
    aug = Augment("Battle Stim", "", attack_bonus=2, health_penalty=5, max_stacks=2)

    assert player.apply_augment(aug) is True
    assert player.attack_power == 12
    assert player.max_health == 95

    assert player.apply_augment(aug) is True
    assert player.attack_power == 14
    assert player.max_health == 90

    # third application should fail due to stack limit
    assert player.apply_augment(aug) is False
    assert player.attack_power == 14
    assert player.max_health == 90


def test_augment_description_includes_combos():
    aug = Augment(
        "Battle Stim",
        "Gain +2 attack, lose 5 max health",
        attack_bonus=2,
        health_penalty=5,
        max_stacks=2,
        combos_with=["Bleed", "Poison"],
    )
    desc = aug.describe()
    assert "Combos with: Bleed, Poison" in desc
