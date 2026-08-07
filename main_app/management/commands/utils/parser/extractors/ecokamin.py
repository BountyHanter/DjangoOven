from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:
    soup = BeautifulSoup(html, "lxml")

    prices_block = soup.select_one(".product__column.content-offer .prices_block")
    if not prices_block:
        return None

    current_price_node = prices_block.select_one(".price:not(.discount)")
    old_price_node = prices_block.select_one(".price.discount")

    price = (
        _extract_number(current_price_node.get("data-value", ""))
        if current_price_node
        else None
    )
    old_price = (
        _extract_number(old_price_node.get("data-value", ""))
        if old_price_node
        else None
    )

    availability = prices_block.select_one("[itemprop='availability']")
    in_stock = None
    if availability and "instock" in availability.get("href", "").lower():
        in_stock = True
    elif availability and "outofstock" in availability.get("href", "").lower():
        in_stock = False

    if price is None and old_price is None and in_stock is None:
        return None

    return PriceResult(
        price=price,
        old_price=old_price,
        in_stock=in_stock,
    )
