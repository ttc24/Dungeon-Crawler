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
    """Hidden hazard that can be spotted and avoided."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        speed = getattr(game.player, "speed", 0)
        perception = getattr(game.player, "perception", 0)
        detect_chance = 0.30 + (speed + perception) * 0.05
        detect_chance = min(0.95, detect_chance)
        if random.random() < detect_chance:
            output_func(_("You spot a faint glyph hinting at a trap."))
            if input_func is input:
                action = "n"
            else:
                prompt = _("Disarm (d) [15 STA] or step around (s)? ")
                action = input_func(prompt).strip().lower()
            if action == "d" and game.player.stamina >= 15:
                game.player.stamina -= 15
                output_func(_("You carefully disarm the trap."))
                game.visited_rooms.add((game.player.x, game.player.y))
                return
            if action == "s":
                output_func(_("You step around the trap, taking extra time."))
                game.visited_rooms.add((game.player.x, game.player.y))
                return
            output_func(_("You hesitate and trigger the trap!"))
        damage = random.randint(5, 20)
        game.player.take_damage(damage, source=_("The Tripwire"))
        output_func(_(f"A trap is sprung! You take {damage} damage."))
        if random.random() < 0.3:
            add_status_effect(game.player, "bleed", 3)
        game.visited_rooms.add((game.player.x, game.player.y))


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
            {"text": _("The walls whisper of an ancient battle.")},
            {"text": _("Scrawled handwriting reads: 'Beware the shadows.'")},
            {"text": _("A faded map hints at deeper treasures.")},
            {
                "text": _(
                    "A margin scribble reveals beetle weak points (+5% hit vs beetles for 10 turns)."
                ),
                "effect": ("beetle_bane", 10),
            },
        ]
        note = random.choice(notes)
        output_func(note["text"])
        if note["text"] not in game.player.codex:
            game.player.codex.append(note["text"])
        if "effect" in note:
            effect, duration = note["effect"]
            add_status_effect(game.player, effect, duration)


class ShrineEvent(BaseEvent):
    """Offer blessings or curses at a shrine."""

    def trigger(self, game: "DungeonBase", input_func=input, output_func=print) -> None:
        output_func(_("You discover a tranquil shrine with two altars."))
        output_func(_("[V] Altar of Valor (+1 STR until next floor)"))
        output_func(_("[W] Altar of Wisdom (+1 INT until next floor)"))
        output_func(_("[P] Pray (60% boon / 40% curse)"))
        choice = input_func(_("Choice: ")).strip().lower()
        if choice == "v":
            game.player.temp_strength += 1
            output_func(_("A surge of might flows through you."))
        elif choice == "w":
            game.player.temp_intelligence += 1
            output_func(_("Your mind feels momentarily sharper."))
        elif choice == "p":
            output_func(_("You kneel and whisper a prayer..."))
            output_func("    _\\/_")
            output_func("     /\\")
            if random.random() < 0.6:
                heal = random.randint(8, 12)
                game.player.health = min(game.player.max_health, game.player.health + heal)
                output_func(_(f"A warm light restores {heal} health."))
            else:
                add_status_effect(game.player, "cursed", 30)
                output_func(_("A dark chill leaves you cursed."))
        else:
            output_func(_("You leave the shrine undisturbed."))


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
