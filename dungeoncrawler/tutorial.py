"""Interactive tutorial for basic game mechanics."""

from __future__ import annotations

from dataclasses import dataclass, field
from gettext import gettext as _

from .input.keys import Action, get_action
from .ui.terminal import Renderer


def run(game_inst, input_func=input, renderer: Renderer | None = None) -> None:
    """Run the tutorial sequence.

    The tutorial walks the player through movement, combat and
    inventory management. It relies on simple text prompts that must
    be acknowledged with the appropriate command before moving on to
    the next section.
    """

    existing = getattr(game_inst, "renderer", None)
    renderer = renderer or (existing if isinstance(existing, Renderer) else None) or Renderer()
    renderer.show_message(_("=== Welcome to the Dungeon Crawler tutorial! ==="))
    renderer.show_message(
        _("Let's begin with movement. Use '1' (left), '2' (right), '3' (up) or '4' (down).")
    )
    while True:
        move = input_func(_("Move: ")).strip()
        action = get_action(move)
        if action in {Action.MOVE_W, Action.MOVE_E, Action.MOVE_N, Action.MOVE_S}:
            renderer.show_message(_("Good job! You can navigate the dungeon using those keys."))
            break
        renderer.show_message(_("Please use one of 1, 2, 3 or 4 to move."))

    renderer.show_message(
        _("Now let's practice combat. Type 'attack' to strike the training dummy.")
    )
    while True:
        action = input_func(_("Action: ")).strip().lower()
        if action == "attack":
            renderer.show_message(_("The dummy falls apart. A solid hit!"))
            break
        renderer.show_message(_("Type 'attack' to perform an attack."))

    renderer.show_message(_("Finally, open your inventory by typing 'inventory'."))
    while True:
        action = input_func(_("Command: ")).strip().lower()
        if action == "inventory":
            renderer.show_message(_("Your empty bag opens. You'll fill it with loot soon enough."))
            break
        renderer.show_message(_("Type 'inventory' to check your belongings."))

    renderer.show_message(_("That's it for the basics. Good luck in the dungeon!"))
    game_inst.tutorial_complete = True


@dataclass
class Tip:
    """A small snippet of instructional text tied to a floor."""

    name: str
    lines: list[str]
    floor: int = 1


BASIC_TIPS = [
    Tip("movement", ["Use the movement keys to explore."], floor=1),
    Tip("combat", ["Engage enemies to gain experience."], floor=2),
]

# ``LEGEND_TIP`` does not store lines directly to keep translations fresh.
LEGEND_TIP = Tip("legend", [], floor=1)

DEFAULT_TIPS = BASIC_TIPS + [LEGEND_TIP]


@dataclass
class TipsManager:
    """Manage display of contextual tips during the game."""

    enabled: bool = True
    seen: set[str] = field(default_factory=set)
    auto_disabled_at: int | None = 2

    def for_floor(self, floor: int) -> list[Tip]:
        """Return unseen tips for ``floor`` respecting disable rules."""

        if not self.enabled:
            return []
        if self.auto_disabled_at is not None and floor > self.auto_disabled_at:
            self.enabled = False
            return []
        return [tip for tip in DEFAULT_TIPS if tip.floor == floor and tip.name not in self.seen]

    def mark_seen(self, tip: Tip) -> None:
        self.seen.add(tip.name)

    def toggle(self) -> None:
        self.enabled = not self.enabled
        if self.enabled:
            # Re-enabling tips disables further auto disabling.
            self.auto_disabled_at = None
