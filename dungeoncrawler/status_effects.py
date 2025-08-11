from __future__ import annotations

from gettext import gettext as _


def apply_status_effects(entity) -> bool:
    """Update ``entity`` based on active status effects.

    Parameters
    ----------
    entity: Any object with ``status_effects`` and ``health`` attributes.

    Returns
    -------
    bool
        ``True`` if the entity's turn should be skipped due to an effect.
    """
    effects = getattr(entity, "status_effects", {})
    skip_turn = False
    is_player = entity.__class__.__name__ == "Player"
    name = entity.name if hasattr(entity, "name") else ""

    if "poison" in effects:
        if effects["poison"] > 0:
            entity.health -= 3
            if is_player:
                print(_("You take 3 poison damage!"))
            else:
                print(_(f"The {name} takes 3 poison damage!"))
            effects["poison"] -= 1
        if effects["poison"] <= 0:
            del effects["poison"]

    if "burn" in effects:
        if effects["burn"] > 0:
            entity.health -= 4
            if is_player:
                print(_("You suffer 4 burn damage!"))
            else:
                print(_(f"The {name} suffers 4 burn damage!"))
            effects["burn"] -= 1
        if effects["burn"] <= 0:
            del effects["burn"]

    if "bleed" in effects:
        if effects["bleed"] > 0:
            entity.health -= 2
            if is_player:
                print(_("You bleed for 2 damage!"))
            else:
                print(_(f"The {name} bleeds for 2 damage!"))
            effects["bleed"] -= 1
        if effects["bleed"] <= 0:
            del effects["bleed"]

    if "freeze" in effects:
        if effects["freeze"] > 0:
            if is_player:
                print(_("You're frozen and lose your turn!"))
            else:
                print(_(f"The {name} is frozen and can't move!"))
            effects["freeze"] -= 1
            skip_turn = True
        if effects["freeze"] <= 0:
            del effects["freeze"]

    if "stun" in effects:
        if effects["stun"] > 0:
            if is_player:
                print(_("You're stunned and can't move!"))
            else:
                print(_(f"The {name} is stunned and can't move!"))
            effects["stun"] -= 1
            skip_turn = True
        if effects["stun"] <= 0:
            del effects["stun"]

    if "shield" in effects:
        effects["shield"] -= 1
        if effects["shield"] <= 0:
            if is_player:
                print(_("Your shield fades."))
            else:
                print(_(f"The {name}'s shield fades."))
            del effects["shield"]

    if "inspire" in effects:
        if effects["inspire"] == 3 and hasattr(entity, "attack_power"):
            entity.attack_power += 3
        effects["inspire"] -= 1
        if effects["inspire"] <= 0:
            if hasattr(entity, "attack_power"):
                entity.attack_power -= 3
            del effects["inspire"]

    return skip_turn
