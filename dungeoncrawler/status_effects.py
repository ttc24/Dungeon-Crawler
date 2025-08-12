from __future__ import annotations

from gettext import gettext as _


EFFECT_INFO = {
    "poison": "Lose 3 HP/turn.",
    "burn": "Lose 4 HP/turn.",
    "bleed": "Lose 2 HP/turn.",
    "freeze": "Cannot act.",
    "stun": "Cannot act.",
    "shield": "Block 5 damage.",
    "inspire": "+3 attack.",
}


def add_status_effect(entity, effect: str, duration: int) -> None:
    """Apply ``effect`` to ``entity`` and announce it."""

    effects = getattr(entity, "status_effects", {})
    effects[effect] = duration
    is_player = entity.__class__.__name__ == "Player"
    desc = EFFECT_INFO.get(effect, "")
    name = getattr(entity, "name", "")
    tag = effect.capitalize()
    if is_player:
        print(_(f"You are {tag} ({duration} turns). {desc}"))
    else:
        print(_(f"The {name} is {tag} ({duration} turns). {desc}"))


def format_status_tags(effects: dict) -> str:
    """Return a compact string of status effect tags."""

    return " ".join(f"[{k.capitalize()}:{v}]" for k, v in effects.items())


def _handle_poison(entity, effects, is_player, name):
    if effects["poison"] > 0:
        entity.health -= 3
        remaining = effects["poison"] - 1
        msg = _(
            f"Poison -3 HP ({remaining} turns left)."
        )
        if is_player:
            print(msg)
        else:
            print(_(f"The {name} {msg.lower()}"))
        effects["poison"] -= 1
    if effects["poison"] <= 0:
        del effects["poison"]
        if is_player:
            print(_("Poison faded."))
        else:
            print(_(f"The {name}'s poison faded."))
    return False


def _handle_burn(entity, effects, is_player, name):
    if effects["burn"] > 0:
        entity.health -= 4
        remaining = effects["burn"] - 1
        msg = _(
            f"Burn -4 HP ({remaining} turns left)."
        )
        if is_player:
            print(msg)
        else:
            print(_(f"The {name} {msg.lower()}"))
        effects["burn"] -= 1
    if effects["burn"] <= 0:
        del effects["burn"]
        if is_player:
            print(_("Burn ended."))
        else:
            print(_(f"The {name}'s burn ended."))
    return False


def _handle_bleed(entity, effects, is_player, name):
    if effects["bleed"] > 0:
        entity.health -= 2
        remaining = effects["bleed"] - 1
        msg = _(
            f"Bleeding -2 HP ({remaining} turns left)."
        )
        if is_player:
            print(msg)
        else:
            print(_(f"The {name} {msg.lower()}"))
        effects["bleed"] -= 1
    if effects["bleed"] <= 0:
        del effects["bleed"]
        if is_player:
            print(_("Bleeding stopped."))
        else:
            print(_(f"The {name}'s bleeding stopped."))
    return False


def _handle_freeze(entity, effects, is_player, name):
    skip_turn = False
    if effects["freeze"] > 0:
        remaining = effects["freeze"] - 1
        msg = _(
            f"Frozen ({remaining} turns left)."
        )
        if is_player:
            print(msg)
        else:
            print(_(f"The {name} is {msg[0].lower() + msg[1:]}"))
        effects["freeze"] -= 1
        skip_turn = True
    if effects["freeze"] <= 0:
        del effects["freeze"]
        if is_player:
            print(_("You thaw out."))
        else:
            print(_(f"The {name} thaws out."))
    return skip_turn


def _handle_stun(entity, effects, is_player, name):
    skip_turn = False
    if effects["stun"] > 0:
        remaining = effects["stun"] - 1
        msg = _(
            f"Stunned ({remaining} turns left)."
        )
        if is_player:
            print(msg)
        else:
            print(_(f"The {name} is {msg[0].lower() + msg[1:]}"))
        effects["stun"] -= 1
        skip_turn = True
    if effects["stun"] <= 0:
        del effects["stun"]
        if is_player:
            print(_("You recover from the stun."))
        else:
            print(_(f"The {name} recovers from the stun."))
    return skip_turn


def _handle_shield(entity, effects, is_player, name):
    effects["shield"] -= 1
    remaining = effects.get("shield", 0)
    if remaining > 0:
        if is_player:
            print(_(f"Shield ({remaining} turns left)."))
        else:
            print(_(f"The {name}'s shield ({remaining} turns left)."))
    if effects["shield"] <= 0:
        if is_player:
            print(_("Your shield fades."))
        else:
            print(_(f"The {name}'s shield fades."))
        del effects["shield"]
    return False


def _handle_inspire(entity, effects, is_player, name):
    if effects["inspire"] == 3 and hasattr(entity, "attack_power"):
        entity.attack_power += 3
    effects["inspire"] -= 1
    remaining = effects.get("inspire", 0)
    if remaining > 0:
        if is_player:
            print(_(f"Inspire ({remaining} turns left)."))
        else:
            print(_(f"The {name} is inspired ({remaining} turns left)."))
    if effects.get("inspire", 0) <= 0:
        if hasattr(entity, "attack_power"):
            entity.attack_power -= 3
        del effects["inspire"]
        if is_player:
            print(_("Inspiration fades."))
        else:
            print(_(f"The {name}'s inspiration fades."))
    return False


STATUS_EFFECT_HANDLERS = {
    "poison": _handle_poison,
    "burn": _handle_burn,
    "bleed": _handle_bleed,
    "freeze": _handle_freeze,
    "stun": _handle_stun,
    "shield": _handle_shield,
    "inspire": _handle_inspire,
}


def apply_status_effects(entity) -> bool:
    """Update ``entity`` based on active status effects."""

    effects = getattr(entity, "status_effects", {})
    skip_turn = False
    is_player = entity.__class__.__name__ == "Player"
    name = entity.name if hasattr(entity, "name") else ""

    for effect in list(effects.keys()):
        handler = STATUS_EFFECT_HANDLERS.get(effect)
        if handler:
            skip_turn = handler(entity, effects, is_player, name) or skip_turn

    return skip_turn
