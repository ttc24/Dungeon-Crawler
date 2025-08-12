"""Event system for random floor encounters."""

from __future__ import annotations

import random
from gettext import gettext as _
from typing import TYPE_CHECKING

from .items import Item
from .status_effects import add_status_effect

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
        output_func(_("You notice taut filament across the path…"))
        if input_func is input:
            choice = "n"
        else:
            choice = input_func(_("Try to disarm? (y/n): ")).strip().lower()
        if choice.startswith("y") and random.random() < 0.5:
            output_func(_("You carefully disarm the trap."))
            return
        damage = random.randint(5, 20)
        game.player.take_damage(damage, source="The Tripwire")
        output_func(_(f"A trap is sprung! You take {damage} damage."))


class FountainEvent(BaseEvent):
    """Cracked fountain that can heal or provide a potion."""

    def __init__(self) -> None:
        self.remaining_uses = 2

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        if self.remaining_uses <= 0:
            output_func(_("The fountain is dry."))
            return
        while self.remaining_uses > 0:
            output_func(_("You find a cracked fountain. The water shimmers."))
            output_func(_("Drink (D) / Bottle (B) / Leave (any other key)"))
            choice = input_func(_("Choice: ")).strip().lower()
            if choice in ("d", "q"):
                heal = random.randint(6, 10)
                game.player.health = min(game.player.max_health, game.player.health + heal)
                output_func(_(f"You feel refreshed and recover {heal} health."))
                roll = random.random()
                if roll < 0.3:
                    add_status_effect(game.player, "blessed", 30)
                elif roll < 0.4:
                    add_status_effect(game.player, "cursed", 30)
            elif choice == "b":
                game.player.inventory.append(Item("Fountain Water", "Restores 4-6 health"))
                output_func(_("You bottle the shimmering water for later."))
            else:
                output_func(_("You leave the fountain untouched."))
                break
            self.remaining_uses -= 1
            if self.remaining_uses <= 0:
                output_func(_("The fountain runs dry."))


class CacheEvent(BaseEvent):
    """Hidden cache that rewards gold."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        gold = random.randint(15, 30)
        game.player.gold += gold
        output_func(_(f"You discover a hidden cache containing {gold} gold."))


class LoreNoteEvent(BaseEvent):
    """Reveal a snippet of lore."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        notes = [
            _("The walls whisper of an ancient battle."),
            _("Scrawled handwriting reads: 'Beware the shadows.'"),
            _("A faded map hints at deeper treasures."),
        ]
        output_func(random.choice(notes))


class ShrineEvent(BaseEvent):
    """Heal the player at a shrine."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        heal = random.randint(8, 12)
        game.player.health = min(game.player.max_health, game.player.health + heal)
        output_func(_(f"A serene shrine restores {heal} health."))


class MiniQuestHookEvent(BaseEvent):
    """Placeholder for mini-quest hooks."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        if getattr(game, "active_quest", None):
            output_func(game.active_quest.flavor)
        else:
            output_func(_("A mysterious figure hints at a quest to come."))


class HazardEvent(BaseEvent):
    """Minor environmental hazard dealing damage."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        damage = random.randint(3, 8)
        game.player.take_damage(damage, source="Environmental Hazard")
        output_func(_(f"Falling debris hits you for {damage} damage."))
