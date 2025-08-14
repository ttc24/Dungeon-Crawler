"""Entry points for running the Dungeon Crawler game.

Character creation begins with just a name on the very first run. As
players reach deeper floors, additional options become available and are
remembered across runs. Classes unlock on floor 1, guilds on floor 2 and
races on floor 3.
"""

import argparse
import json
from gettext import gettext as _

from . import tutorial
from .config import Config, load_config
from .constants import RUN_FILE
from .dungeon import DungeonBase
from .entities import Player, SKILL_DEFS
from .i18n import set_language


def _load_unlocks():
    unlocks = {"class": False, "guild": False, "race": False}
    if RUN_FILE.exists():
        try:
            with open(RUN_FILE) as f:
                unlocks.update(json.load(f).get("unlocks", {}))
        except (IOError, json.JSONDecodeError):
            pass
    return unlocks


def build_character(input_func=input, output_func=print):
    """Interactively construct a :class:`Player`.

    Depending on previously unlocked features the player may also choose a
    class, guild and race during character creation.
    """

    name = ""
    while not name:
        name = input_func(_("Enter your name: ")).strip()
        if not name:
            output_func(_("Name cannot be blank."))

    player = Player(name)
    unlocks = _load_unlocks()

    def prompt_class():
        output_func(_("It's time to choose your class! This choice is permanent."))
        classes = {
            "1": ("Warrior", _("Balanced fighter")),
            "2": ("Mage", _("Master of spells")),
            "3": ("Rogue", _("Stealthy attacker")),
            "4": ("Cleric", _("Holy healer")),
            "5": ("Barbarian", _("Brutal strength")),
            "6": ("Ranger", _("Skilled hunter")),
            "7": ("Druid", _("Nature's guardian")),
            "8": ("Sorcerer", _("Chaotic caster")),
            "9": ("Monk", _("Disciplined striker")),
            "10": ("Warlock", _("Pact magic")),
            "11": ("Necromancer", _("Master of the dead")),
            "12": ("Shaman", _("Spiritual guide")),
            "13": ("Alchemist", _("Potion expert")),
        }
        names = {v[0].lower(): k for k, v in classes.items()}
        skill_tip = ", ".join(f"{s['name']} ({s['cost']} stamina)" for s in SKILL_DEFS)
        for key, (name, desc) in classes.items():
            output_func(_(f"{key}. {name} - {desc}"))
        output_func(_(f"Skills: {skill_tip}"))
        aliases = {"wiz": "mage"}
        while True:
            try:
                raw = input_func(_("Class: ")).strip().lower()
            except (EOFError, OSError):
                return
            choice = None
            if raw.isdigit() and raw in classes:
                choice = raw
            else:
                key = aliases.get(raw, raw)
                if key in names:
                    choice = names[key]
            if choice is None:
                output_func(_("Please enter a number (1–13) or a valid class name."))
                continue
            player.choose_class(classes[choice][0])
            break

    def prompt_guild():
        if player.guild:
            return
        output_func(_("Guilds now accept new members! This choice is permanent."))
        guilds = {
            "1": ("Warriors' Guild", _("Bonus Health")),
            "2": ("Mages' Guild", _("Bonus Attack")),
            "3": ("Rogues' Guild", _("Faster Skills")),
            "4": ("Healers' Circle", _("Extra Vitality")),
            "5": ("Shadow Brotherhood", _("Heavy Strikes")),
            "6": ("Arcane Order", _("Arcane Mastery")),
        }
        skill_tip = ", ".join(f"{s['name']} ({s['cost']} stamina)" for s in SKILL_DEFS)
        for key, (name, desc) in guilds.items():
            output_func(_(f"{key}. {name} - {desc}"))
        output_func(_(f"Skills: {skill_tip}"))
        choice = input_func(_("Join which guild? (1-6 or skip): "))
        if choice in guilds:
            player.join_guild(guilds[choice][0])

    def prompt_race():
        if player.race:
            return
        output_func(_("New races are available to you! This choice is permanent."))
        races = {
            "1": ("Human", _("Versatile")),
            "2": ("Elf", _("Graceful")),
            "3": ("Dwarf", _("Stout")),
            "4": ("Orc", _("Savage")),
            "5": ("Gnome", _("Clever")),
            "6": ("Tiefling", _("Fiendish")),
            "7": ("Dragonborn", _("Draconic")),
            "8": ("Goblin", _("Sneaky")),
        }
        skill_tip = ", ".join(f"{s['name']} ({s['cost']} stamina)" for s in SKILL_DEFS)
        for key, (name, desc) in races.items():
            output_func(_(f"{key}. {name} - {desc}"))
        output_func(_(f"Skills: {skill_tip}"))
        choice = input_func(_("Choose your race: "))
        race = races.get(choice)
        if race:
            player.choose_race(race[0])

    if unlocks.get("class"):
        prompt_class()
    if unlocks.get("guild"):
        prompt_guild()
    if unlocks.get("race"):
        prompt_race()

    output_func(_("Welcome {name}! Your journey is just beginning.").format(name=player.name))
    return player


def main(argv=None, input_func=input, output_func=print, cfg: Config | None = None):
    """Run the game with optional command line arguments.

    Parameters
    ----------
    argv:
        Optional sequence of arguments to parse instead of ``sys.argv``.
    input_func, output_func:
        Hooks used primarily for testing to simulate user interaction.
    cfg:
        Pre-loaded configuration.  When ``None`` the configuration is loaded
        from ``config.json`` automatically.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-tutorial",
        action="store_true",
        help=_("Do not run the interactive tutorial"),
    )
    parser.add_argument("--lang", help=_("Language code for translations"))
    args = parser.parse_args(argv)

    set_language(args.lang)

    cfg = cfg or load_config()
    game = DungeonBase(cfg.screen_width, cfg.screen_height)
    cont = input_func(_("Load existing save? (y/n): ")).strip().lower()
    if cont == "y":
        floor = game.load_game()
        try:
            output_func(_("Resuming on Floor {floor}.").format(floor=floor))
        except Exception:
            pass
        # Fallback if the save didn't actually produce a player
        if getattr(game, "player", None) is None:
            output_func(_("No valid save found. Starting a new game…"))
            game.player = build_character(input_func=input_func, output_func=output_func)
            if not args.skip_tutorial and not game.tutorial_complete:
                tutorial.run(game)
    else:
        game.player = build_character(input_func=input_func, output_func=output_func)
        if args.skip_tutorial:
            game.tutorial_complete = True
        elif not game.tutorial_complete:
            tutorial.run(game)
    game.play_game()


if __name__ == "__main__":
    main()
