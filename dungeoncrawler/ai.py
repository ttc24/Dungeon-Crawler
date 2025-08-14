import json
import random
from pathlib import Path


class AggressiveAI:
    """Simple AI that always chooses to attack."""

    def choose_action(self, enemy, player):
        return "attack"


class DefensiveAI:
    """AI that prioritizes defense when health is low."""

    def choose_action(self, enemy, player):
        if enemy.health <= enemy.max_health // 2 and "shield" not in enemy.status_effects:
            return "defend"
        return "attack"


class IntentAI:
    """Weighted three-state controller for enemy behaviour.

    Each enemy configured with this AI chooses between Aggressive,
    Defensive and Unpredictable intents every turn according to the
    provided weights.  The chosen intent is *telegraphed* to the player in
    advance so they can react during their turn. Aggressive intents may
    unleash a ``heavy_attack`` for increased damage, while Unpredictable
    intents can result in a ``wild_attack`` that trades accuracy for a
    powerful blow.

    Parameters
    ----------
    aggressive: int
        Relative weight for selecting an aggressive action.
    defensive: int
        Relative weight for selecting a defensive action.
    unpredictable: int
        Relative weight for selecting an unpredictable action.
    """

    TELEGRAPHS = {
        "Goblin": {
            "aggressive": "Goblin winds up a heavy strike…",
            "defensive": "Goblin raises its guard.",
            "unpredictable": "The Goblin grins wildly, unpredictable…",
        },
        "Beetle": {
            "defensive": "Beetle curls into its shell.",
        },
        "Acolyte": {
            "aggressive": "Acolyte begins channeling (interrupt with 8+ damage).",
        },
    }

    def __init__(self, aggressive=1, defensive=1, unpredictable=1):
        self.weights = {
            "aggressive": aggressive,
            "defensive": defensive,
            "unpredictable": unpredictable,
        }

    # ------------------------------------------------------------------
    def choose_intent(self, enemy, player):
        """Select the next action and telegraph it to the player.

        Returns
        -------
        tuple[str, str, str]
            ``(action, intent, message)`` describing what the enemy will do on
            its next turn, the intent category (``"Aggressive"``,
            ``"Defensive"`` or ``"Unpredictable"``) and the text used to
            foreshadow that intent.
        """

        intents = list(self.weights.keys())
        weights = list(self.weights.values())
        intent_key = random.choices(intents, weights=weights, k=1)[0]

        # Map intents to actions and default telegraphs
        action = "attack"
        message = {
            "aggressive": f"The {enemy.name} winds up for a heavy strike…",
            "defensive": f"The {enemy.name} raises its guard.",
            "unpredictable": f"The {enemy.name} wavers unpredictably…",
        }[intent_key]

        if intent_key == "aggressive" and getattr(enemy, "heavy_cd", 0) == 0:
            action = "heavy_attack"
        elif intent_key == "defensive" and enemy.health <= enemy.max_health // 3:
            action = "defend"
        elif intent_key == "unpredictable":
            action = random.choice(["wild_attack", "defend"])

        # Custom telegraphs for specific enemy archetypes
        telegraphs = self.TELEGRAPHS.get(enemy.name, {})
        message = telegraphs.get(intent_key, message)

        intent = intent_key.capitalize()
        return action, intent, message

    # Backwards compatibility for older saves/tests
    plan_next = choose_intent


# Extend telegraphs for enemies defined in floors.json
try:
    _floors_path = Path(__file__).resolve().parents[1] / "data" / "floors.json"
    with _floors_path.open() as _f:
        _floors = json.load(_f)
    for _cfg in _floors.values():
        for _name in _cfg.get("enemies", []):
            IntentAI.TELEGRAPHS.setdefault(
                _name,
                {
                    "aggressive": f"{_name} prepares a vicious strike.",
                    "defensive": f"{_name} braces for incoming attacks.",
                    "unpredictable": f"{_name} shifts unpredictably.",
                },
            )
except FileNotFoundError:
    pass


# Default archetype weights for enemies that use IntentAI
ARCHETYPES = {
    "Goblin": {"aggressive": 3, "defensive": 1, "unpredictable": 1},
    "Beetle": {"aggressive": 1, "defensive": 3, "unpredictable": 1},
    "Acolyte": {"aggressive": 2, "defensive": 1, "unpredictable": 2},
}

# Telegraphs for bosses to foreshadow their unique mechanics
IntentAI.TELEGRAPHS.update(
    {
        "Bone Tyrant": {
            "aggressive": "Bone Tyrant hefts its club for a crushing blow.",
            "defensive": "Bone Tyrant knits stray bones into a shield.",
            "unpredictable": "Bone Tyrant rattles erratically, bones spiraling.",
        },
        "Inferno Golem": {
            "aggressive": "Inferno Golem's core flares for a magma punch.",
            "defensive": "Inferno Golem's lava skin hardens into rock.",
            "unpredictable": "Flames dance wildly around the Inferno Golem.",
        },
        "Shadow Reaver": {
            "aggressive": "Shadow Reaver fades then lunges from the darkness.",
            "defensive": "Shadow Reaver cloaks itself in shadow.",
            "unpredictable": "Shadow Reaver flickers unpredictably.",
        },
        "Void Serpent": {
            "aggressive": "Void Serpent coils, void energy crackling.",
            "defensive": "Void Serpent slips into an ethereal stance.",
            "unpredictable": "Void Serpent warps space erratically.",
        },
        "Grave Monarch": {
            "aggressive": "Grave Monarch raises its scythe for a soul-cleaving arc.",
            "defensive": "Grave Monarch summons tombstone shields.",
            "unpredictable": "Grave Monarch mutters necrotic rites unpredictably.",
        },
        "Frost Warden": {
            "aggressive": "Frost Warden gathers icy winds for a chilling strike.",
            "defensive": "Frost Warden encases itself in ice.",
            "unpredictable": "Frost Warden's blizzard swirls unpredictably.",
        },
        "Ember Lord": {
            "aggressive": "Ember Lord ignites embers for a blazing lash.",
            "defensive": "Ember Lord surrounds itself with a ring of fire.",
            "unpredictable": "Sparks whirl erratically around the Ember Lord.",
        },
        "Glacier Fiend": {
            "aggressive": "Glacier Fiend raises frozen claws for a heavy swing.",
            "defensive": "Glacier Fiend reinforces its icy hide.",
            "unpredictable": "Glacier Fiend crackles, ice shards darting.",
        },
        "Storm Reaper": {
            "aggressive": "Storm Reaper crackles with lightning, ready to cleave.",
            "defensive": "Storm Reaper channels static into a barrier.",
            "unpredictable": "Storm Reaper's aura flickers with erratic sparks.",
        },
        "Doom Bringer": {
            "aggressive": "Doom Bringer roars, axe poised for devastation.",
            "defensive": "Doom Bringer braces behind its massive axe.",
            "unpredictable": "Doom Bringer's stance shifts unpredictably.",
        },
        "Arcane Sentinel": {
            "aggressive": "Arcane Sentinel charges a beam of raw energy.",
            "defensive": "Arcane Sentinel conjures a shimmering ward.",
            "unpredictable": "Arcane Sentinel's runes flare unpredictably.",
        },
        "Blight Matron": {
            "aggressive": "Blight Matron readies a venomous lash.",
            "defensive": "Blight Matron oozes toxins as a protective veil.",
            "unpredictable": "Blight Matron's spores drift unpredictably.",
        },
        "Chaos Djinn": {
            "aggressive": "Chaos Djinn whirls up a storm of blades.",
            "defensive": "Chaos Djinn twists into a protective whirlwind.",
            "unpredictable": "Chaos Djinn's form distorts unpredictably.",
        },
        "Dread Colossus": {
            "aggressive": "Dread Colossus raises its hammer for a quake.",
            "defensive": "Dread Colossus plants its feet, stone skin thickening.",
            "unpredictable": "Dread Colossus lurches in unpredictable stomps.",
        },
        "Ethereal Harvester": {
            "aggressive": "Ethereal Harvester sweeps its scythe in a ghostly arc.",
            "defensive": "Ethereal Harvester fades partially out of phase.",
            "unpredictable": "Ethereal Harvester flickers between realms.",
        },
        "Feral Juggernaut": {
            "aggressive": "Feral Juggernaut snarls, muscles bulging for a charge.",
            "defensive": "Feral Juggernaut hunkers down, hide toughening.",
            "unpredictable": "Feral Juggernaut paces erratically.",
        },
        "Gloom Shade": {
            "aggressive": "Gloom Shade reaches out with grasping darkness.",
            "defensive": "Gloom Shade melds with surrounding shadows.",
            "unpredictable": "Gloom Shade's silhouette warps unpredictably.",
        },
        "Hex King": {
            "aggressive": "Hex King chants a ruinous spell.",
            "defensive": "Hex King weaves a lattice of cursed sigils.",
            "unpredictable": "Hex King's curses spiral unpredictably.",
        },
    }
)
