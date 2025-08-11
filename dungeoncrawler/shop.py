"""Shop and inventory management routines."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .items import Item, Weapon

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from .dungeon import DungeonBase


def shop(game: "DungeonBase") -> None:
    """Interact with the shop allowing the player to buy or sell items."""

    print("Welcome to the Shop!")
    print(f"Gold: {game.player.gold}")
    for i, item in enumerate(game.shop_items, 1):
        price = item.price if isinstance(item, Weapon) else 10
        print(f"{i}. {item.name} - {price} Gold")
    sell_option = len(game.shop_items) + 1
    exit_option = sell_option + 1
    print(f"{sell_option}. Sell Items")
    print(f"{exit_option}. Exit")

    choice = input("Choose an option:")
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(game.shop_items):
            item = game.shop_items[choice - 1]
            price = item.price if isinstance(item, Weapon) else 10
            if game.player.gold >= price:
                game.player.collect_item(item)
                game.player.gold -= price
                print(f"You bought {item.name}.")
            else:
                print("Not enough gold.")
        elif choice == sell_option:
            sell_items(game)
        elif choice == exit_option:
            print("Leaving the shop.")
        else:
            print("Invalid choice.")
    else:
        print("Invalid input.")


def get_sale_price(item):
    """Return the sale price for ``item`` or ``None`` if unsellable."""

    if isinstance(item, Weapon):
        price = getattr(item, "price", 0)
        if price > 0:
            return price // 2
        return None
    if isinstance(item, Item):
        return 5
    return None


def sell_items(game: "DungeonBase") -> None:
    """Sell items from the player's inventory."""

    if not game.player.inventory:
        print("You have nothing to sell.")
        return

    print("Your Items:")
    for i, item in enumerate(game.player.inventory, 1):
        sale_price = get_sale_price(item)
        if sale_price is None:
            print(f"{i}. {item.name} - Cannot sell")
        else:
            print(f"{i}. {item.name} - {sale_price} Gold")
    print(f"{len(game.player.inventory)+1}. Back")

    choice = input("Sell what?")
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(game.player.inventory):
            item = game.player.inventory[choice - 1]
            sale_price = get_sale_price(item)
            if sale_price is None:
                print("You can't sell that item.")
                return
            confirm = input(f"Sell {item.name} for {sale_price} gold? (y/n) ")
            if confirm.lower() == "y":
                game.player.inventory.pop(choice - 1)
                game.player.gold += sale_price
                print(f"You sold {item.name}.")
        elif choice == len(game.player.inventory) + 1:
            return
        else:
            print("Invalid choice.")
    else:
        print("Invalid input.")


def show_inventory(game: "DungeonBase") -> None:
    """Display the player's inventory and allow equipping weapons."""

    if not game.player.inventory:
        print("Your inventory is empty.")
        return

    print("Your Inventory:")
    for i, item in enumerate(game.player.inventory, 1):
        equipped = " (Equipped)" if item == game.player.weapon else ""
        print(f"{i}. {item.name}{equipped} - {item.description}")

    choice = input("Enter item number to equip weapon, or press Enter to go back: ")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(game.player.inventory):
            item = game.player.inventory[idx]
            if isinstance(item, Weapon):
                game.player.equip_weapon(item)
            else:
                print("You can only equip weapons.")
        else:
            print("Invalid selection.")

