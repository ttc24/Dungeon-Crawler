"""Interactive tutorial for basic game mechanics."""

from __future__ import annotations

from gettext import gettext as _

from .input.keys import Action, get_action
from .ui.terminal import Renderer


def run(game, input_func=input, renderer: Renderer | None = None) -> None:
    """Run the tutorial sequence.

    The tutorial walks the player through movement, combat and
    inventory management. It relies on simple text prompts that must
    be acknowledged with the appropriate command before moving on to
    the next section.
    """

    renderer = renderer or getattr(game, "renderer", Renderer())
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
    game.tutorial_complete = True


if __name__ == "__main__":  # pragma: no cover - convenience script
    from .config import load_config
    from .dungeon import DungeonBase
    from .main import build_character

    cfg = load_config()
    game = DungeonBase(cfg.screen_width, cfg.screen_height)
    game.player = build_character()
    run(game)
