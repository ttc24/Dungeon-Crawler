import json

from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.main import build_character


def test_build_character_save_manipulation(tmp_path, monkeypatch):
    run_path = tmp_path / "run.json"
    run_path.write_text(
        json.dumps(
            {
                "total_runs": 1,
                "unlocks": {"class": True, "guild": True, "race": True},
                "max_floor": 1,
            }
        )
    )
    monkeypatch.setattr("dungeoncrawler.constants.RUN_FILE", run_path)
    monkeypatch.setattr("dungeoncrawler.main.RUN_FILE", run_path)
    inputs = iter(["Bob", "1"])  # name, class
    player = build_character(input_func=lambda _: next(inputs), output_func=lambda _m: None)
    assert player.class_type == "Warrior"
    assert player.guild is None
    assert player.race is None


def test_offer_methods_require_correct_floor():
    dungeon = DungeonBase(5, 5)
    dungeon.player = Player("hero")
    dungeon.unlocks = {"class": True, "guild": True, "race": True}

    dungeon.current_floor = 1
    dungeon.offer_guild(input_func=lambda _: "1")
    dungeon.offer_race(input_func=lambda _: "2")
    assert dungeon.player.guild is None
    assert dungeon.player.race is None

    dungeon.offer_class(input_func=lambda _: "1")
    assert dungeon.player.class_type == "Warrior"

    dungeon.current_floor = 2
    dungeon.offer_guild(input_func=lambda _: "1")
    assert dungeon.player.guild == "Warriors' Guild"

    dungeon.current_floor = 3
    dungeon.offer_race(input_func=lambda _: "2")
    assert dungeon.player.race == "Elf"
