from __future__ import annotations

import random
from gettext import gettext as _

EFFECT_INFO = {
    "poison": "Lose 3 HP/turn.",
    "burn": "Lose 4 HP/turn.",
    "bleed": "Lose 2 HP/turn.",
    "freeze": "Cannot act.",
    "stun": "Cannot act.",
    "shield": "Block 5 damage.",
    "inspire": "+3 attack.",
    "guard": "Incoming damage -40%. Next attack +10% hit.",
    "stagger": "-20% hit.",
    "blessed": "+10% hit chance.",
    "cursed": "-5% hit chance.",
    "beetle_bane": "+5% hit chance vs beetles.",
    "blood_torrent": "Lose 1 HP per stack each turn.",
    "blood_scent": "Enemies can track you.",
    "compression_sickness": "Speed and accuracy reduced.",
    "mana_lock": "Spell costs +50%. Cleanses may fail.",
    "dull_wards": "Shields 30% weaker; crits can't pierce.",
    "entropic_debt": "Lose 1% max HP per stack each turn.",
    "spiteful_reflection": "20% chance to reflect debuffs.",
    "brood_bloom": "Spawns a broodling when it erupts.",
    "miasma_aura": "Healing halved.",
    "temporal_lag": "15% chance to repeat last action, wasting the turn.",
    "haste_dysphoria": "Speed bonuses beyond 25% invert to penalties.",
    "fester_mark": "Overheal causes lingering damage.",
    "soul_tax": "-1 attack per stack; +5% loot chance.",
    "spotlight_ping": "Enemies know your location.",
    "audience_fatigue": "Repeated ability use reduces damage and healing.",
    "creeping_corruption": "Vision reduced; positive buffs suppressed.",
}

# Multipliers applied to status effect durations based on enemy rarity.
# Higher rarity foes resist negative conditions for fewer turns.
RARITY_STATUS_RESISTANCE = {
    "rare": 0.8,
    "elite": 0.5,
}


DEBUFFS = {
    "poison",
    "burn",
    "bleed",
    "freeze",
    "stun",
    "cursed",
    "blood_torrent",
    "blood_scent",
    "compression_sickness",
    "entropic_debt",
    "brood_bloom",
    "miasma_aura",
    "temporal_lag",
    "haste_dysphoria",
    "fester_mark",
    "soul_tax",
    "spotlight_ping",
    "audience_fatigue",
    "creeping_corruption",
}


def add_status_effect(entity, effect: str, duration: int, source=None, _reflected=False) -> None:
    """Apply ``effect`` to ``entity`` and announce it."""

    # ``status_effects`` may not be defined on some lightweight objects used
    # in tests or when the function is called in isolation.  Using
    # ``getattr`` with a default dictionary would update a temporary object
    # and the applied effect would be lost.  Ensure the attribute exists on
    # the entity so subsequent calls can operate on the same dictionary.
    effects = getattr(entity, "status_effects", None)
    if effects is None:
        effects = {}
        setattr(entity, "status_effects", effects)
    rarity = getattr(entity, "rarity", "common")
    modifier = RARITY_STATUS_RESISTANCE.get(rarity, 1.0)
    if rarity == "elite" and getattr(entity, "floor", 1) < 10:
        modifier = 1.0
    duration = max(1, int(duration * modifier))
    effects[effect] = duration
    is_player = entity.__class__.__name__ == "Player"
    desc = EFFECT_INFO.get(effect, "")
    name = getattr(entity, "name", "")
    tag = effect.capitalize()
    if is_player:
        print(_(f"You are {tag} ({duration} turns). {desc}"))
    else:
        print(_(f"The {name} is {tag} ({duration} turns). {desc}"))
    if (
        source is not None
        and not _reflected
        and "spiteful_reflection" in effects
        and effect in DEBUFFS
        and random.random() < 0.2
    ):
        add_status_effect(source, effect, duration, _reflected=True)


def format_status_tags(effects: dict) -> str:
    """Return a compact string of status effect tags."""

    return " ".join(f"[{k.capitalize()}:{v}]" for k, v in effects.items())


def adjust_skill_cost(entity, base_cost: int) -> int:
    """Return stamina cost adjusted by ``mana_lock`` and suppression rings."""

    effects = getattr(entity, "status_effects", {})
    if "mana_lock" not in effects:
        return base_cost
    multiplier = 1.5
    trinket = getattr(entity, "trinket", None)
    if trinket and getattr(trinket, "name", "") == "Suppression Ring":
        multiplier = 1.0
        if random.random() < 0.25:
            print(_("The Suppression Ring overheats and crumbles!"))
            entity.trinket = None
    return int(base_cost * multiplier)


def cleansing_fails(entity) -> bool:
    """Return ``True`` if cleanse or dispel attempts fizzle under Mana Lock."""

    effects = getattr(entity, "status_effects", {})
    return "mana_lock" in effects and random.random() < 0.25


def shield_block(entity, base_block: int) -> int:
    """Return shield value adjusted by ``dull_wards`` if present."""

    effects = getattr(entity, "status_effects", {})
    if "dull_wards" in effects:
        return int(base_block * 0.7)
    return base_block


def temporal_lag_trigger(entity, state, action, resource_attr: str, cost: int) -> bool:
    """Handle Temporal Lag, possibly repeating an action.

    If the effect triggers, refund ``cost`` to ``resource_attr`` on ``entity`` and
    queue the repeated action on a random target. Returns ``True`` if the turn
    was consumed by lag.
    """

    effects = getattr(entity, "status_effects", {})
    if "temporal_lag" not in effects or not action or action in {"wait", "defend"}:
        return False
    if random.random() >= 0.15:
        return False
    if cost:
        setattr(entity, resource_attr, getattr(entity, resource_attr) + cost)
    targets = [entity] + list(getattr(state, "enemies", []))
    state.game.repeat_action = action
    state.game.repeat_target = random.choice(targets) if targets else None
    state.game.last_action = None
    return True


def _handle_poison(entity, effects, is_player, name):
    if effects["poison"] > 0:
        entity.health -= 3
        remaining = effects["poison"] - 1
        msg = _(f"Poison -3 HP ({remaining} turns left).")
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
        damage = 4
        traits = getattr(entity, "traits", [])
        if "fire_vulnerable" in traits:
            damage *= 2
        entity.health -= damage
        remaining = effects["burn"] - 1
        msg = _(f"Burn -{damage} HP ({remaining} turns left).")
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
        msg = _(f"Bleeding -2 HP ({remaining} turns left).")
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
        msg = _(f"Frozen ({remaining} turns left).")
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
        msg = _(f"Stunned ({remaining} turns left).")
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


def _handle_blessed(entity, effects, is_player, name):
    effects["blessed"] -= 1
    remaining = effects.get("blessed", 0)
    if remaining > 0:
        if is_player:
            print(_(f"Blessed ({remaining} turns left)."))
        else:
            print(_(f"The {name} is blessed ({remaining} turns left)."))
    if effects["blessed"] <= 0:
        del effects["blessed"]
        if is_player:
            print(_("Blessing fades."))
        else:
            print(_(f"The {name}'s blessing fades."))
    return False


def _handle_cursed(entity, effects, is_player, name):
    effects["cursed"] -= 1
    remaining = effects.get("cursed", 0)
    if remaining > 0:
        if is_player:
            print(_(f"Cursed ({remaining} turns left)."))
        else:
            print(_(f"The {name} is cursed ({remaining} turns left)."))
    if effects["cursed"] <= 0:
        del effects["cursed"]
        if is_player:
            print(_("Curse fades."))
        else:
            print(_(f"The {name}'s curse fades."))
    return False


def _handle_beetle_bane(entity, effects, is_player, name):
    effects["beetle_bane"] -= 1
    remaining = effects.get("beetle_bane", 0)
    if remaining > 0:
        if is_player:
            print(_(f"Beetle Bane ({remaining} turns left)."))
        else:
            print(_(f"The {name} studies beetle weaknesses ({remaining} turns left)."))
    if effects.get("beetle_bane", 0) <= 0:
        del effects["beetle_bane"]
        if is_player:
            print(_("Your beetle lore fades."))
        else:
            print(_(f"The {name}'s beetle lore fades."))
    return False


def _handle_blood_torrent(entity, effects, is_player, name):
    stacks = effects.get("blood_torrent", 0)
    if stacks > 0:
        entity.health -= stacks
        msg = _(f"Blood Torrent -{stacks} HP.")
        if is_player:
            print(msg)
        else:
            print(_(f"The {name} {msg.lower()}"))
    return False


def _handle_blood_scent(entity, effects, is_player, name):
    effects["blood_scent"] -= 1
    if effects["blood_scent"] <= 0:
        del effects["blood_scent"]
    return False


def _handle_compression_sickness(entity, effects, is_player, name):
    if not getattr(entity, "_compression_sickness_applied", False):
        entity._compression_sickness_applied = True
        entity._compression_prev_speed = getattr(entity, "speed", 0)
        entity.speed = int(entity.speed * 0.9)
    effects["compression_sickness"] -= 1
    remaining = effects.get("compression_sickness", 0)
    if remaining > 0:
        if is_player:
            print(_(f"Compression Sickness ({remaining} turns left)."))
        else:
            print(_(f"The {name} reels ({remaining} turns left)."))
    if effects.get("compression_sickness", 0) <= 0:
        entity.speed = getattr(entity, "_compression_prev_speed", entity.speed)
        entity._compression_sickness_applied = False
        effects.pop("compression_sickness", None)
        if is_player:
            print(_("Compression Sickness fades."))
        else:
            print(_(f"The {name} steadies."))
    return False


def _handle_brood_bloom(entity, effects, is_player, name):
    duration = effects.get("brood_bloom", 0)
    if duration <= 0:
        effects.pop("brood_bloom", None)
        return False
    effects["brood_bloom"] -= 1
    if effects["brood_bloom"] <= 0:
        callback = getattr(entity, "brood_spawn", None)
        if callable(callback):
            callback(entity)
        prev = getattr(entity, "brood_bloom_stack", duration)
        new_dur = prev // 2
        if new_dur > 0:
            effects["brood_bloom"] = new_dur
            entity.brood_bloom_stack = new_dur
        else:
            effects.pop("brood_bloom", None)
            entity.brood_bloom_stack = 0
    return False


def _handle_miasma_aura(entity, effects, is_player, name):
    if not getattr(entity, "_miasma_active", False):
        entity._miasma_active = True
        entity._miasma_prev_heal = getattr(entity, "heal_multiplier", 1.0)
        entity.heal_multiplier = entity._miasma_prev_heal * 0.5
    effects["miasma_aura"] -= 1
    if effects["miasma_aura"] <= 0:
        entity.heal_multiplier = getattr(entity, "_miasma_prev_heal", 1.0)
        entity._miasma_active = False
        effects.pop("miasma_aura", None)
    return False


def _handle_entropic_debt(entity, effects, is_player, name):
    stacks = effects.get("entropic_debt", 0)
    if stacks <= 0:
        effects.pop("entropic_debt", None)
        return False
    max_hp = getattr(entity, "max_health", getattr(entity, "health", 0))
    damage = max(1, int(max_hp * 0.01 * stacks))
    entity.health -= damage
    msg = _(f"Entropic Debt -{damage} HP ({stacks} stacks).")
    if is_player:
        print(msg)
    else:
        print(_(f"The {name} {msg.lower()}"))
    return False


def _handle_spiteful_reflection(entity, effects, is_player, name):
    return False


def _handle_temporal_lag(entity, effects, is_player, name):
    return False


def _handle_haste_dysphoria(entity, effects, is_player, name):
    base = getattr(entity, "_haste_dysphoria_base", None)
    if base is None:
        entity._haste_dysphoria_base = getattr(entity, "speed", 0)
        return False
    if getattr(entity, "speed", 0) > base * 1.25:
        ratio = entity.speed / base - 1
        entity.speed = max(1, int(base * (1 - ratio)))
    return False


def _handle_fester_mark(entity, effects, is_player, name):
    damage = getattr(entity, "_fester_mark_damage", 0)
    if damage > 0:
        entity.health -= damage
        remaining = effects.get("fester_mark", 0) - 1
        msg = _(f"Fester Mark -{damage} HP ({remaining} turns left).")
        if is_player:
            print(msg)
        else:
            print(_(f"The {name} {msg.lower()}"))
    effects["fester_mark"] -= 1
    if effects["fester_mark"] <= 0:
        effects.pop("fester_mark", None)
        entity._fester_mark_damage = 0
        if is_player:
            print(_("The mark fades."))
        else:
            print(_(f"The {name}'s mark fades."))
    return False


def _handle_spotlight_ping(entity, effects, is_player, name):
    """Spotlight ping persists until manually removed."""
    # No automatic duration reduction; effect remains until cleared by items.
    effects["spotlight_ping"] = effects.get("spotlight_ping", 1)
    return False


def _handle_creeping_corruption(entity, effects, is_player, name):
    if effects["creeping_corruption"] > 0:
        if not getattr(entity, "_corruption_active", False):
            entity._corruption_active = True
            entity._corruption_prev_vision = getattr(entity, "vision", 0)
            entity.vision = max(1, entity._corruption_prev_vision - 1)
        effects["creeping_corruption"] -= 1
        for buff in ("blessed", "inspire"):
            effects.pop(buff, None)
        msg = _("Corruption clouds your vision.")
        if is_player:
            print(msg)
        else:
            print(_(f"The {name} is engulfed in corruption."))
    else:
        if getattr(entity, "_corruption_active", False):
            entity.vision = getattr(entity, "_corruption_prev_vision", entity.vision)
            delattr(entity, "_corruption_active")
        effects.pop("creeping_corruption", None)
        if is_player:
            print(_("The corruption recedes."))
        else:
            print(_(f"The {name}'s corruption fades."))
    return False


def _handle_audience_fatigue(entity, effects, is_player, name):
    """Decay Audience Fatigue stacks and update penalties."""
    timers = getattr(entity, "_audience_fatigue_timers", [])
    if not timers:
        effects.pop("audience_fatigue", None)
        entity.__dict__.pop("_audience_fatigue_mult", None)
        return False
    new_timers = []
    for t in timers:
        t -= 1
        if t > 0:
            new_timers.append(t)
    entity._audience_fatigue_timers = new_timers
    if new_timers:
        stacks = len(new_timers)
        effects["audience_fatigue"] = stacks
        entity._audience_fatigue_mult = 1 - 0.1 * stacks
    else:
        effects.pop("audience_fatigue", None)
        entity.__dict__.pop("_audience_fatigue_mult", None)
    return False


def _handle_soul_tax(entity, effects, is_player, name):
    timers = getattr(entity, "_soul_tax_timers", [])
    if not timers:
        effects.pop("soul_tax", None)
        return False
    new_timers = []
    state = getattr(entity, "_soul_tax_state", None)
    for t in timers:
        t -= 1
        if t <= 0:
            entity.attack_power += 1
            if state is not None:
                state.config.loot_mult = max(
                    getattr(entity, "_soul_tax_base_loot", state.config.loot_mult),
                    state.config.loot_mult - 0.05,
                )
        else:
            new_timers.append(t)
    entity._soul_tax_timers = new_timers
    if new_timers:
        effects["soul_tax"] = max(new_timers)
    else:
        effects.pop("soul_tax", None)
    return False


def clear_soul_tax(entity):
    timers = getattr(entity, "_soul_tax_timers", [])
    if not timers:
        return
    state = getattr(entity, "_soul_tax_state", None)
    restored = len(timers)
    entity.attack_power += restored
    if state is not None:
        state.config.loot_mult = getattr(entity, "_soul_tax_base_loot", state.config.loot_mult)
    entity._soul_tax_timers = []
    effects = getattr(entity, "status_effects", {})
    effects.pop("soul_tax", None)


STATUS_EFFECT_HANDLERS = {
    "poison": _handle_poison,
    "burn": _handle_burn,
    "bleed": _handle_bleed,
    "freeze": _handle_freeze,
    "stun": _handle_stun,
    "shield": _handle_shield,
    "inspire": _handle_inspire,
    "blessed": _handle_blessed,
    "cursed": _handle_cursed,
    "beetle_bane": _handle_beetle_bane,
    "blood_torrent": _handle_blood_torrent,
    "blood_scent": _handle_blood_scent,
    "compression_sickness": _handle_compression_sickness,
    "entropic_debt": _handle_entropic_debt,
    "spiteful_reflection": _handle_spiteful_reflection,
    "brood_bloom": _handle_brood_bloom,
    "miasma_aura": _handle_miasma_aura,
    "temporal_lag": _handle_temporal_lag,
    "haste_dysphoria": _handle_haste_dysphoria,
    "fester_mark": _handle_fester_mark,
    "soul_tax": _handle_soul_tax,
    "spotlight_ping": _handle_spotlight_ping,
    "audience_fatigue": _handle_audience_fatigue,
    "creeping_corruption": _handle_creeping_corruption,
}


def apply_status_effects(entity) -> bool:
    """Update ``entity`` based on active status effects."""
    effects = getattr(entity, "status_effects", None)
    if effects is None:
        effects = {}
        setattr(entity, "status_effects", effects)
        return False
    skip_turn = False
    is_player = entity.__class__.__name__ == "Player"
    name = entity.name if hasattr(entity, "name") else ""

    for effect in list(effects.keys()):
        handler = STATUS_EFFECT_HANDLERS.get(effect)
        if handler:
            skip_turn = handler(entity, effects, is_player, name) or skip_turn

    return skip_turn
