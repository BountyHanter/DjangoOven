from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:

    soup = BeautifulSoup(html, "lxml")

    product = soup.select_one(".js-product-single")
    if not product:
        return None

    price = None
    old_price = None

    # ---- цена ----
    price_node = product.select_one(".js-product-price")

    if price_node:
        price = _extract_number(price_node.get_text())

    # ---- старая цена ----
    old_price_node = product.select_one(".js-store-prod-price-old-val")

    if old_price_node:
        old_price = _extract_number(old_price_node.get_text())

    if price is None and old_price is None:
        return None

    return PriceResult(
        price=price,
        old_price=old_price,
    )