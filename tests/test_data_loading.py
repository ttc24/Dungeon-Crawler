import json
from pathlib import Path
import json

import dungeoncrawler.data as data_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.events import MerchantEvent


def test_shop_items_reflect_json_change(tmp_path):
    items_path = Path(__file__).resolve().parents[1] / "data" / "items.json"
    original = items_path.read_text(encoding="utf-8")
    try:
        payload = json.loads(original)
        payload["shop"].append({"type": "Item", "name": "UnitTest Trinket", "description": "Tmp"})
        items_path.write_text(json.dumps(payload), encoding="utf-8")
        data_module.load_items.cache_clear()
        game = DungeonBase(4, 4)
        assert any(i.name == "UnitTest Trinket" for i in game.shop_items)
    finally:
        items_path.write_text(original, encoding="utf-8")
        data_module.load_items.cache_clear()


def test_random_events_reflect_json_change(monkeypatch):
    events_path = Path(__file__).resolve().parents[1] / "data" / "events_extended.json"
    original = events_path.read_text(encoding="utf-8")
    try:
        payload = json.loads(original)
        payload["random"] = {"MerchantEvent": 1.0}
        payload["dungeon"] = {}
        events_path.write_text(json.dumps(payload), encoding="utf-8")
        data_module.load_event_defs.cache_clear()
        game = DungeonBase(4, 4)
        called = {}

        def fake_trigger(self, game, input_func=input, output_func=print):
            called["cls"] = self.__class__.__name__

        monkeypatch.setattr(MerchantEvent, "trigger", fake_trigger)
        game.trigger_random_event(1)
        assert called["cls"] == "MerchantEvent"
    finally:
        events_path.write_text(original, encoding="utf-8")
        data_module.load_event_defs.cache_clear()
