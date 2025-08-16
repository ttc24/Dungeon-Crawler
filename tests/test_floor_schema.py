import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator, ValidationError

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schemas" / "floor.json").read_text())
FLOOR_FILES = sorted((ROOT / "data" / "floors").glob("*.json"))


@pytest.mark.parametrize("floor_path", FLOOR_FILES, ids=lambda p: p.name)
def test_floor_files_conform_to_schema(floor_path):
    data = json.loads(floor_path.read_text())
    data.pop("$schema", None)
    Draft7Validator(SCHEMA).validate(data)


def test_missing_hooks_field_is_invalid():
    """Floor entries lacking the required hooks list should fail validation."""
    invalid = {
        "id": "00",
        "name": "Invalid",
        "map": [],
        "rule_mods": {},
        "objective": {},
        "spawns": [],
        "ui": {},
    }
    with pytest.raises(ValidationError):
        Draft7Validator(SCHEMA).validate(invalid)
