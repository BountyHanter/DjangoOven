from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:

    soup = BeautifulSoup(html, "lxml")

    price_block = soup.select_one("p.price")
    if not price_block:
        return None

    price = None
    old_price = None

    # ---- цена со скидкой ----
    new_price_node = price_block.select_one("ins .amount")
    old_price_node = price_block.select_one("del .amount")

    if new_price_node:
        price = _extract_number(new_price_node.get_text())

    if old_price_node:
        old_price = _extract_number(old_price_node.get_text())

    # ---- обычная цена ----
    if price is None:
        regular_node = price_block.select_one(".amount")
        if regular_node:
            price = _extract_number(regular_node.get_text())

    if price is None and old_price is None:
        return None

    return PriceResult(
        price=price,
        old_price=old_price,
    )