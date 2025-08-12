"""Shop and inventory management routines."""

from __future__ import annotations

from gettext import gettext as _
from typing import TYPE_CHECKING

from .constants import INVALID_KEY_MSG
from .items import Item, Weapon

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from .dungeon import DungeonBase


def shop(
    game: "DungeonBase",
    input_func=input,
    output_func=print,
) -> None:
    """Interact with the shop allowing the player to buy or sell items."""

    output_func(_("Welcome to the Shop!"))
    output_func(_(f"Gold: {game.player.gold}"))
    for i, item in enumerate(game.shop_items, 1):
        price = item.price if isinstance(item, Weapon) else 10
        output_func(_(f"{i}. {item.name} - {price} Gold"))
    sell_option = len(game.shop_items) + 1
    exit_option = sell_option + 1
    output_func(_(f"{sell_option}. Sell Items"))
    output_func(_(f"{exit_option}. Exit"))

    choice = input_func(_("Choose an option:"))
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(game.shop_items):
            item = game.shop_items[choice - 1]
            price = item.price if isinstance(item, Weapon) else 10
            if game.player.gold >= price:
                game.player.collect_item(item)
                game.player.gold -= price
                output_func(_(f"You bought {item.name}."))
            else:
                output_func(_("Not enough gold."))
        elif choice == sell_option:
            sell_items(game, input_func=input_func, output_func=output_func)
        elif choice == exit_option:
            output_func(_("Leaving the shop."))
        else:
            output_func(_(INVALID_KEY_MSG))
    else:
        output_func(_(INVALID_KEY_MSG))


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


def sell_items(
    game: "DungeonBase",
    input_func=input,
    output_func=print,
) -> None:
    """Sell items from the player's inventory."""

    if not game.player.inventory:
        output_func(_("You have nothing to sell."))
        return

    output_func(_("Your Items:"))
    for i, item in enumerate(game.player.inventory, 1):
        sale_price = get_sale_price(item)
        if sale_price is None:
            output_func(_(f"{i}. {item.name} - Cannot sell"))
        else:
            output_func(_(f"{i}. {item.name} - {sale_price} Gold"))
    output_func(_(f"{len(game.player.inventory)+1}. Back"))

    choice = input_func(_("Sell what?"))
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(game.player.inventory):
            item = game.player.inventory[choice - 1]
            sale_price = get_sale_price(item)
            if sale_price is None:
                output_func(_("You can't sell that item."))
                return
            confirm = input_func(_(f"Sell {item.name} for {sale_price} gold? (y/n) "))
            if confirm.lower() == "y":
                game.player.inventory.pop(choice - 1)
                game.player.gold += sale_price
                output_func(_(f"You sold {item.name}."))
        elif choice == len(game.player.inventory) + 1:
            return
        else:
            output_func(_(INVALID_KEY_MSG))
    else:
        output_func(_(INVALID_KEY_MSG))


def show_inventory(
    game: "DungeonBase",
    input_func=input,
    output_func=print,
) -> None:
    """Display the player's inventory and allow equipping weapons."""

    if not game.player.inventory:
        output_func(_("Your inventory is empty."))
        return

    output_func(_("Your Inventory:"))
    for i, item in enumerate(game.player.inventory, 1):
        equipped = " (Equipped)" if item == game.player.weapon else ""
        output_func(_(f"{i}. {item.name}{equipped} - {item.description}"))

    choice = input_func(
        _("Enter item number to equip weapon, or press Enter to go back: ")
    )
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(game.player.inventory):
            item = game.player.inventory[idx]
            if isinstance(item, Weapon):
                game.player.equip_weapon(item)
            else:
                output_func(_("You can only equip weapons."))
        else:
            output_func(_(INVALID_KEY_MSG))
