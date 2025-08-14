"""Tests ensuring defense values are considered in combat."""

from dungeoncrawler.combat import enemy_turn
from dungeoncrawler.core.combat import resolve_player_action
from dungeoncrawler.core.entity import Entity as CoreEntity
from dungeoncrawler.entities import Armor, Enemy, Player


class DummyRenderer:
    def handle_event(self, event) -> None:  # pragma: no cover - no logic
        pass


def test_enemy_turn_respects_player_armor(monkeypatch):
    """Enemy attacks should be reduced by the player's armor defense."""

    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: 1)
    player = Player("Hero")
    player.armor = Armor("Plate", "", defense=3)
    enemy = Enemy("Goblin", 10, 5, 0, 0)
    start = player.health

    enemy_turn(enemy, player, DummyRenderer())

    assert player.health == start - 2  # 5 attack - 3 defense


def test_player_attack_respects_enemy_defense(monkeypatch):
    """Player damage should be reduced by enemy defense."""

    monkeypatch.setattr("dungeoncrawler.core.combat.random.randint", lambda a, b: 1)
    player = Player("Hero")
    enemy = Enemy("Goblin", 10, 0, 3, 0)

    p_entity = CoreEntity(
        player.name,
        {
            "health": player.health,
            "attack": getattr(player, "attack_power", 0),
            "max_health": player.max_health,
            "defense": getattr(player.armor, "defense", 0),
            "speed": getattr(player, "speed", 0),
        },
    )
    e_entity = CoreEntity(
        enemy.name,
        {
            "health": enemy.health,
            "attack": getattr(enemy, "attack_power", 0),
            "max_health": enemy.max_health,
            "defense": getattr(enemy, "defense", 0),
            "speed": getattr(enemy, "speed", 0),
        },
    )

    resolve_player_action(p_entity, e_entity, "attack")

    assert e_entity.stats["health"] == enemy.health - (player.attack_power - enemy.defense)
