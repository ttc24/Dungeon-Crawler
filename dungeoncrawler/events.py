"""Event system for random floor encounters."""

from __future__ import annotations

import random
from gettext import gettext as _
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .dungeon import DungeonBase


class BaseEvent:
    """Abstract base class for all events."""

    def trigger(
        self, game: "DungeonBase", input_func=input, output_func=print
    ) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class MerchantEvent(BaseEvent):
    """Open the in-game shop."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        game.shop(input_func=input_func, output_func=output_func)


class PuzzleEvent(BaseEvent):
    """Present a riddle that rewards gold when solved."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        riddle, answer = random.choice(game.riddles)
        output_func(_("A sage presents a riddle:\n") + riddle)
        response = input_func(_("Answer: ")).strip().lower()
        if response == answer:
            reward = 50
            output_func(_(f"Correct! You receive {reward} gold."))
            game.player.gold += reward
        else:
            output_func(_("Incorrect! The sage vanishes in disappointment."))


class TrapEvent(BaseEvent):
    """Inflict random damage to the player."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        damage = random.randint(5, 20)
        game.player.take_damage(damage, source="The Tripwire")
        output_func(_(f"A trap is sprung! You take {damage} damage."))
