from __future__ import annotations

import random
from gettext import gettext as _
from typing import Dict, List

# Word pools used to generate flavor text for special room types.
# Having the data in a dedicated module makes it easy to localize
# or expand in the future without touching game logic.
ROOM_FLAVOR_POOLS: Dict[str, Dict[str, List[str]]] = {
    "Glittering Vault": {
        "adjectives": ["glittering", "shimmering", "dusty"],
        "nouns": ["vault", "chamber", "cache"],
        "verbs": [
            "beckons with ancient riches",
            "gleams with forgotten coins",
            "radiates a faint glow",
        ],
    },
    "Booby-Trapped Passage": {
        "adjectives": ["narrow", "foreboding", "cramped"],
        "nouns": ["passage", "corridor", "hallway"],
        "verbs": [
            "is littered with suspicious mechanisms",
            "hides pressure plates",
            "promises peril at every step",
        ],
    },
    "Cursed Hall": {
        "adjectives": ["shadowy", "gloomy", "whispering"],
        "nouns": ["hall", "chamber", "gallery"],
        "verbs": [
            "seems alive with malevolent intent",
            "echoes with unseen whispers",
            "makes your skin crawl",
        ],
    },
    "Sealed Gate": {
        "adjectives": ["massive", "ancient", "rune-covered"],
        "nouns": ["gate", "door", "portal"],
        "verbs": [
            "bars your path",
            "hums with dormant power",
            "looms immovably",
        ],
    },
    "Hidden Niche": {
        "adjectives": ["small", "dusty", "concealed"],
        "nouns": ["niche", "alcove", "hollow"],
        "verbs": [
            "hides something of value",
            "holds a faint glimmer",
            "beckons the curious",
        ],
    },
    "Silent Chamber": {
        "adjectives": ["silent", "dusty", "forgotten"],
        "nouns": ["chamber", "room", "space"],
        "verbs": [
            "lies untouched by time",
            "echoes with your footsteps",
            "breathes an eerie calm",
        ],
    },
    "Sacred Sanctuary": {
        "adjectives": ["serene", "peaceful", "hallowed"],
        "nouns": ["sanctuary", "shrine", "haven"],
        "verbs": [
            "radiates soothing warmth",
            "fills you with calm",
            "offers respite",
        ],
    },
}


def generate_room_flavor(room_type: str) -> str:
    """Return a short, randomized description for ``room_type``."""
    pools = ROOM_FLAVOR_POOLS.get(room_type)
    if not pools:
        return ""
    adjective = random.choice(pools["adjectives"])
    noun = random.choice(pools["nouns"])
    verb = random.choice(pools["verbs"])
    return _(f"The {adjective} {noun} {verb}.")
