"""Typed event objects produced by core game mechanics."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from .data import load_events

EVENT_DATA = load_events()


@dataclass
class Event:
    """Base class for all core events."""

    message: str


@dataclass
class AttackResolved(Event):
    """Result of a combat attack action."""

    attacker: str
    defender: str
    damage: int
    defeated: bool
    attack: int = 0
    defense: int = 0
    critical: bool = False


@dataclass
class StatusApplied(Event):
    """A temporary status was applied to an entity."""

    target: str
    status: str
    duration: int
    value: int = 0


@dataclass
class IntentTelegraphed(Event):
    """An enemy revealed its next action before taking it."""

    actor: str
    intent: str


@dataclass
class TileDiscovered(Event):
    """A new map tile has been revealed to the player."""

    x: int
    y: int


@dataclass
class ItemGained(Event):
    """An item was added to an entity's inventory."""

    owner: str
    item: str
    amount: int = 1


# ---------------------------------------------------------------------------
# Interactive feature handlers
# ---------------------------------------------------------------------------


@dataclass
class Fountain:
    """Simple fountain feature allowing the player to drink or bottle water.

    Parameters
    ----------
    uses:
        How many times the fountain can be used before drying up.
    bless_chance / curse_chance:
        Probabilities applied when drinking.  A blessing or curse is modelled
        as a :class:`StatusApplied` event and the status flag is appended to the
        player's ``status`` list.
    """

    uses: int = EVENT_DATA.get("fountain", {}).get("uses", 2)
    bless_chance: float = EVENT_DATA.get("fountain", {}).get("bless_chance", 0.3)
    curse_chance: float = EVENT_DATA.get("fountain", {}).get("curse_chance", 0.1)
    rarity: str = EVENT_DATA.get("fountain", {}).get("rarity", "common")

    def interact(self, player, action: str) -> List[Event]:
        """Return a list of events produced by interacting with the fountain."""

        events: List[Event] = []
        if self.uses <= 0:
            return [Event("The fountain is dry.")]

        action = action.lower()
        if action == "drink":
            heal = random.randint(6, 10)
            hp = player.stats.get("health", 0)
            max_hp = player.stats.get("max_health", hp)
            player.stats["health"] = min(max_hp, hp + heal)
            events.append(
                StatusApplied(
                    f"{player.name} drinks from the fountain and heals {heal} health.",
                    player.name,
                    "healed",
                    0,
                    value=heal,
                )
            )
            roll = random.random()
            if roll < self.bless_chance:
                player.status.append("blessed")
                events.append(
                    StatusApplied(f"{player.name} feels blessed.", player.name, "blessed", 30)
                )
            elif roll < self.bless_chance + self.curse_chance:
                player.status.append("cursed")
                events.append(
                    StatusApplied(f"{player.name} feels cursed.", player.name, "cursed", 30)
                )
        elif action == "bottle":
            player.inventory.append("fountain_water")
            events.append(
                ItemGained(
                    f"{player.name} bottles some fountain water.",
                    player.name,
                    "fountain_water",
                )
            )
        else:
            events.append(Event("You leave the fountain untouched."))
            return events

        self.uses -= 1
        if self.uses <= 0:
            events.append(Event("The fountain runs dry."))
        return events


def handle_fountain(player, action: str, fountain: Optional[Fountain] = None) -> List[Event]:
    """Convenience wrapper around :class:`Fountain.interact`.

    ``fountain`` may be provided to persist remaining uses between calls.
    """

    fountain = fountain or Fountain()
    return fountain.interact(player, action)


@dataclass
class LockedCache:
    """Locked cache requiring a key to open.

    The first time the cache is inspected without the key a callback is
    invoked to spawn the missing key elsewhere in the dungeon.  A breadcrumb
    style :class:`Event` message is returned to hint at its location.
    """

    loot: str = EVENT_DATA.get("locked_cache", {}).get("loot", "credits")
    key_name: str = EVENT_DATA.get("locked_cache", {}).get("key_name", "cache_key")
    opened: bool = False
    key_spawned: bool = False
    rarity: str = EVENT_DATA.get("locked_cache", {}).get("rarity", "rare")

    def interact(self, player, spawn_key: Callable[[str], None]) -> List[Event]:
        events: List[Event] = []
        if self.opened:
            return [Event("The cache is empty.")]

        if self.key_name in player.inventory:
            player.inventory.remove(self.key_name)
            player.inventory.append(self.loot)
            self.opened = True
            events.append(
                ItemGained(
                    f"{player.name} unlocks the cache and finds {self.loot}.",
                    player.name,
                    self.loot,
                )
            )
            return events

        events.append(Event("The cache is locked."))
        if not self.key_spawned:
            spawn_key(self.key_name)
            self.key_spawned = True
            events.append(Event("You notice scratches leading away as if something was dragged."))
        return events


def handle_locked_cache(
    player, spawn_key: Callable[[str], None], cache: Optional[LockedCache] = None
) -> List[Event]:
    """Interact with a :class:`LockedCache` and return generated events."""

    cache = cache or LockedCache()
    return cache.interact(player, spawn_key)


@dataclass
class LoreNote:
    """Lore note that may also grant a temporary status effect."""

    text: str
    effect: Optional[Tuple[str, int]] = None

    def interact(self, player) -> List[Event]:
        events = [Event(self.text)]
        codex = getattr(player, "codex", None)
        if codex is not None and self.text not in codex:
            codex.append(self.text)
        if self.effect:
            status, duration = self.effect
            player.status.append(status)
            events.append(
                StatusApplied(f"{player.name} gains {status}.", player.name, status, duration)
            )
        return events


def handle_lore_note(player, text: str, effect: Optional[Tuple[str, int]] = None) -> List[Event]:
    """Convenience wrapper around :class:`LoreNote.interact`."""

    note = LoreNote(text, effect)
    return note.interact(player)
