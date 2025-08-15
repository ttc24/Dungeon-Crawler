import dungeoncrawler.dungeon as dungeon_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Companion, Player
from dungeoncrawler.items import Item, Weapon


def test_save_and_load(tmp_path, monkeypatch):
    save_path = tmp_path / "save.json"
    monkeypatch.setattr(dungeon_module, "SAVE_FILE", str(save_path))

    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Saver")
    dungeon.player.credits = 42
    potion = Item("Potion", "Heals")
    dungeon.player.collect_item(potion)
    sword = Weapon("Sword", "Sharp", 3, 5)
    sword.effect = "burn"
    dungeon.player.collect_item(sword)
    dungeon.player.equip_weapon(sword)
    ally = Companion("Wolf", "boost")
    dungeon.player.companions.append(ally)
    dungeon.save_game(floor=3)

    new_dungeon = DungeonBase(1, 1)
    floor = new_dungeon.load_game()
    assert floor == 3
    assert new_dungeon.player.name == "Saver"
    assert new_dungeon.player.credits == 42
    assert len(new_dungeon.player.inventory) == 1
    loaded_item = new_dungeon.player.inventory[0]
    assert isinstance(loaded_item, Item)
    assert loaded_item.name == "Potion"
    assert new_dungeon.player.weapon.name == "Sword"
    assert new_dungeon.player.weapon.effect == "burn"
    assert all(it.name != "Sword" for it in new_dungeon.player.inventory)
    assert len(new_dungeon.player.companions) == 1
    loaded_companion = new_dungeon.player.companions[0]
    assert loaded_companion.name == "Wolf"
    assert loaded_companion.effect == "boost"
