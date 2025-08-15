import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schemas" / "floor.json").read_text())
FLOOR_FILES = sorted((ROOT / "data" / "floors").glob("*.json"))

@pytest.mark.parametrize("floor_path", FLOOR_FILES, ids=lambda p: p.name)
def test_floor_files_conform_to_schema(floor_path):
    data = json.loads(floor_path.read_text())
    data.pop("$schema", None)
    Draft7Validator(SCHEMA).validate(data)
