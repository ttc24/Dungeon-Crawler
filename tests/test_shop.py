import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dungeoncrawler import shop as shop_module
from dungeoncrawler.dungeon import DungeonBase
from dungeoncrawler.entities import Player
from dungeoncrawler.items import Item, Weapon


def test_shop_purchase():
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Buyer")
    dungeon.player.gold = 20
    shop_module.shop(dungeon, input_func=lambda _: "1", output_func=lambda _msg: None)
    assert dungeon.player.gold == 10
    assert any(item.name == "Health Potion" for item in dungeon.player.inventory)


def test_sell_weapon():
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Seller")
    weapon = Weapon("Sword", "A sharp sword", 10, 15, 40)
    dungeon.player.collect_item(weapon)
    inputs = iter(["1", "y"])
    shop_module.sell_items(
        dungeon, input_func=lambda _: next(inputs), output_func=lambda _msg: None
    )
    assert dungeon.player.gold == 20
    assert weapon not in dungeon.player.inventory


def test_sell_item():
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Seller")
    potion = Item("Health Potion", "Restores 20 health")
    dungeon.player.collect_item(potion)
    inputs = iter(["1", "y"])
    shop_module.sell_items(
        dungeon, input_func=lambda _: next(inputs), output_func=lambda _msg: None
    )
    assert dungeon.player.gold == 5
    assert potion not in dungeon.player.inventory


def test_sell_unsellable():
    dungeon = DungeonBase(1, 1)
    dungeon.player = Player("Seller")
    rare_weapon = Weapon("Elven Longbow", "Bow", 15, 25, 0)
    dungeon.player.collect_item(rare_weapon)
    shop_module.sell_items(dungeon, input_func=lambda _: "1", output_func=lambda _msg: None)
    assert dungeon.player.gold == 0
    assert rare_weapon in dungeon.player.inventory


def test_shop_inventory_deterministic():
    random.seed(0)
    dungeon = DungeonBase(1, 1)
    random.seed(0)
    dungeon.restock_shop()
    first = [item.name for item in dungeon.shop_inventory]
    random.seed(0)
    dungeon.restock_shop()
    second = [item.name for item in dungeon.shop_inventory]
    assert first == second
