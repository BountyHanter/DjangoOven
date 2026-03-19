from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.schemas import PriceResult
from main_app.management.commands.utils.parser.extract_number import _extract_number


def extract_price(html: str) -> PriceResult | None:

    soup = BeautifulSoup(html, "lxml")

    form = soup.select_one("form.product")
    if not form:
        return None

    price = None
    old_price = None
    in_stock = False

    # ---- цена ----
    price_node = form.select_one(".product__price-cur")
    if price_node:
        price = _extract_number(price_node.get_text())

    # ---- старая цена ----
    old_price_node = form.select_one(".product__price-old")
    if old_price_node:
        old_price = _extract_number(old_price_node.get_text())

    # ---- наличие ----
    if form.select_one(".text___available"):
        in_stock = True

    if form.select_one(".text___not-available"):
        in_stock = False

    if price is None and old_price is None:
        return None

    return PriceResult(
        price=price,
        old_price=old_price,
        in_stock=in_stock
    )