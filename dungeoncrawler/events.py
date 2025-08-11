"""Event system for random floor encounters."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING
from gettext import gettext as _

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .dungeon import DungeonBase


class BaseEvent:
    """Abstract base class for all events."""

    def trigger(self, game: "DungeonBase") -> None:  # pragma: no cover - interface
        raise NotImplementedError


class MerchantEvent(BaseEvent):
    """Open the in-game shop."""

    def trigger(self, game: "DungeonBase") -> None:
        game.shop()


class PuzzleEvent(BaseEvent):
    """Present a riddle that rewards gold when solved."""

    def trigger(self, game: "DungeonBase") -> None:
        riddle, answer = random.choice(game.riddles)
        print(_("A sage presents a riddle:\n") + riddle)
        response = input(_("Answer: ")).strip().lower()
        if response == answer:
            reward = 50
            print(_(f"Correct! You receive {reward} gold."))
            game.player.gold += reward
        else:
            print(_("Incorrect! The sage vanishes in disappointment."))


class TrapEvent(BaseEvent):
    """Inflict random damage to the player."""

    def trigger(self, game: "DungeonBase") -> None:
        damage = random.randint(5, 20)
        game.player.take_damage(damage)
        print(_(f"A trap is sprung! You take {damage} damage."))
