from __future__ import annotations

from gettext import gettext as _


def _handle_poison(entity, effects, is_player, name):
    if effects["poison"] > 0:
        entity.health -= 3
        if is_player:
            print(_("You take 3 poison damage!"))
        else:
            print(_(f"The {name} takes 3 poison damage!"))
        effects["poison"] -= 1
    if effects["poison"] <= 0:
        del effects["poison"]
    return False


def _handle_burn(entity, effects, is_player, name):
    if effects["burn"] > 0:
        entity.health -= 4
        if is_player:
            print(_("You suffer 4 burn damage!"))
        else:
            print(_(f"The {name} suffers 4 burn damage!"))
        effects["burn"] -= 1
    if effects["burn"] <= 0:
        del effects["burn"]
    return False


def _handle_bleed(entity, effects, is_player, name):
    if effects["bleed"] > 0:
        entity.health -= 2
        if is_player:
            print(_("You bleed for 2 damage!"))
        else:
            print(_(f"The {name} bleeds for 2 damage!"))
        effects["bleed"] -= 1
    if effects["bleed"] <= 0:
        del effects["bleed"]
    return False


def _handle_freeze(entity, effects, is_player, name):
    skip_turn = False
    if effects["freeze"] > 0:
        if is_player:
            print(_("You're frozen and lose your turn!"))
        else:
            print(_(f"The {name} is frozen and can't move!"))
        effects["freeze"] -= 1
        skip_turn = True
    if effects["freeze"] <= 0:
        del effects["freeze"]
    return skip_turn


def _handle_stun(entity, effects, is_player, name):
    skip_turn = False
    if effects["stun"] > 0:
        if is_player:
            print(_("You're stunned and can't move!"))
        else:
            print(_(f"The {name} is stunned and can't move!"))
        effects["stun"] -= 1
        skip_turn = True
    if effects["stun"] <= 0:
        del effects["stun"]
    return skip_turn


def _handle_shield(entity, effects, is_player, name):
    effects["shield"] -= 1
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
    if effects["inspire"] <= 0:
        if hasattr(entity, "attack_power"):
            entity.attack_power -= 3
        del effects["inspire"]
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
