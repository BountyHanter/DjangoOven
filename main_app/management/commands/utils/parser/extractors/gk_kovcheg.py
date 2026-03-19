from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:

    soup = BeautifulSoup(html, "lxml")

    form = soup.select_one("form.ms2_form")
    if not form:
        return None

    # ---- нет в наличии ----
    if form.select_one(".outStock"):
        return PriceResult(in_stock=False, is_active=False)

    # ---- цена со скидкой ----
    price_node = form.select_one(".price")
    old_price_node = form.select_one(".oldPrice")

    price = None
    old_price = None

    if price_node:
        price = _extract_number("".join(price_node.stripped_strings))

    if old_price_node:
        old_price = _extract_number("".join(old_price_node.stripped_strings))

    if price is None and old_price is None:
        return None

    return PriceResult(
        price=price,
        old_price=old_price,
    )