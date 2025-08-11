from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.items import Item, Weapon


def test_shop_purchase(monkeypatch):
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Buyer")
    dungeon.player.gold = 20
    monkeypatch.setattr("builtins.input", lambda _: "1")
    dungeon.shop()
    assert dungeon.player.gold == 10
    assert any(item.name == "Health Potion" for item in dungeon.player.inventory)


def test_sell_weapon(monkeypatch):
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Seller")
    weapon = Weapon("Sword", "A sharp sword", 10, 15, 40)
    dungeon.player.collect_item(weapon)
    inputs = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    dungeon.sell_items()
    assert dungeon.player.gold == 20
    assert weapon not in dungeon.player.inventory


def test_sell_item(monkeypatch):
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Seller")
    potion = Item("Health Potion", "Restores 20 health")
    dungeon.player.collect_item(potion)
    inputs = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    dungeon.sell_items()
    assert dungeon.player.gold == 5
    assert potion not in dungeon.player.inventory


def test_sell_unsellable(monkeypatch):
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Seller")
    rare_weapon = Weapon("Elven Longbow", "Bow", 15, 25, 0)
    dungeon.player.collect_item(rare_weapon)
    monkeypatch.setattr("builtins.input", lambda _: "1")
    dungeon.sell_items()
    assert dungeon.player.gold == 0
    assert rare_weapon in dungeon.player.inventory
