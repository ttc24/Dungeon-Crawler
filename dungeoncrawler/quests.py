from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .entities import Enemy
from .items import Item


@dataclass
class Quest:
    """Base quest type storing goal, reward and flavor text."""

    description: str
    reward: int
    flavor: str

    def status(self, game) -> str:  # pragma: no cover - simple formatting
        return self.description

    def is_complete(self, game) -> bool:  # pragma: no cover - interface
        return False


class FetchQuest(Quest):
    """Retrieve a specific item from the dungeon."""

    def __init__(self, item: Item, location: Tuple[int, int], reward: int, flavor: str):
        super().__init__(f"Fetch {item.name}", reward, flavor)
        self.item = item
        self.location = location
        self.hint_given = False

    def is_complete(self, game) -> bool:
        return game.player.has_item(self.item.name)

    def status(self, game) -> str:
        return f"{self.description} ({'1/1' if self.is_complete(game) else '0/1'})"


class HuntQuest(Quest):
    """Defeat a specific enemy."""

    def __init__(self, enemy: Enemy, reward: int, flavor: str):
        super().__init__(f"Slay {enemy.name}", reward, flavor)
        self.enemy = enemy

    def is_complete(self, game) -> bool:
        return not self.enemy.is_alive()

    def status(self, game) -> str:
        return f"{self.description} ({'done' if self.is_complete(game) else 'alive'})"


@dataclass
class EscortNPC:
    """Passive NPC used for escort quests.

    The NPC only tracks its position within the dungeon and whether it has
    started following the player.  Using a dataclass keeps the implementation
    lightweight while still providing a clear structure for the test-suite to
    interact with.
    """

    name: str
    x: int = 0
    y: int = 0
    following: bool = False


class EscortQuest(Quest):
    """Guide a helpless NPC to the exit."""

    def __init__(self, npc: EscortNPC, reward: int, flavor: str):
        super().__init__(f"Escort {npc.name}", reward, flavor)
        self.npc = npc

    def is_complete(self, game) -> bool:
        return (self.npc.x, self.npc.y) == game.exit_coords and (
            game.player.x,
            game.player.y,
        ) == game.exit_coords

    def status(self, game) -> str:
        if self.is_complete(game):
            return f"{self.description} (complete)"
        return f"{self.description} (en route)"
