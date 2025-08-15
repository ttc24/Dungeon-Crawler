import json
import shutil
from pathlib import Path

from dungeoncrawler import data


def test_swapping_floor_json_changes_behavior(tmp_path, monkeypatch):
    original = data.load_floor_definitions()["01"].name

    temp_data = tmp_path
    src_floors = Path(data.DATA_DIR) / "floors"
    shutil.copytree(src_floors, temp_data / "floors")

    modified = temp_data / "floors" / "01_intro.json"
    contents = json.loads(modified.read_text())
    contents["name"] = "Altered Floor"
    modified.write_text(json.dumps(contents))

    monkeypatch.setattr(data, "DATA_DIR", temp_data)
    data.load_floor_definitions.cache_clear()
    altered = data.load_floor_definitions()["01"].name

    assert altered == "Altered Floor"
    assert altered != original
