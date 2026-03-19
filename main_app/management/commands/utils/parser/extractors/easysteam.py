from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:

    soup = BeautifulSoup(html, "lxml")

    price_node = soup.select_one(".js-detail-price")
    if not price_node:
        return None

    price = None

    # сначала пробуем нормальное число из атрибута
    if price_node.has_attr("data-base-price"):
        price = int(price_node["data-base-price"])
    else:
        price = _extract_number(price_node.get_text())

    return PriceResult(
        price=price,
        old_price=None,
    )