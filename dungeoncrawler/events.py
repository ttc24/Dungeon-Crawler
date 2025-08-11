"""Event classes used by the dungeon crawler game.

The events encapsulate special encounters that may occur when
descending to new floors. Each event exposes a :meth:`trigger` method
that operates on the :class:`~dungeoncrawler.dungeon.DungeonBase`
instance passed to it.
"""

from __future__ import annotations

import random

from .constants import RIDDLES


class BaseEvent:
    """Base class for floor events."""

    name = "base"

    def trigger(self, dungeon: "DungeonBase") -> None:  # pragma: no cover - interface
        raise NotImplementedError


class MerchantEvent(BaseEvent):
    """A travelling merchant appears and opens a shop."""

    name = "Merchant"

    def trigger(self, dungeon: "DungeonBase") -> None:
        dungeon.shop()


class PuzzleEvent(BaseEvent):
    """A riddle challenge that rewards gold if answered correctly."""

    name = "Puzzle"

    def trigger(self, dungeon: "DungeonBase") -> None:
        riddle = random.choice(RIDDLES)
        print(riddle["question"])
        response = input("Answer: ").strip().lower()
        if response == riddle["answer"]:
            reward = 50
            print(f"Correct! You receive {reward} gold.")
            dungeon.player.gold += reward
        else:
            print("Incorrect! The puzzle resets.")


class TrapEvent(BaseEvent):
    """A simple trap that harms the player."""

    name = "Trap"

    def trigger(self, dungeon: "DungeonBase") -> None:
        damage = 10
        print(f"A hidden trap springs! You take {damage} damage.")
        dungeon.player.take_damage(damage)


EVENT_TYPES = {cls.name: cls for cls in (MerchantEvent, PuzzleEvent, TrapEvent)}
