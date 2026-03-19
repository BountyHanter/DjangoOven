from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:
    soup = BeautifulSoup(html, "lxml")

    price_tag = soup.select_one(".price__new-val")

    price = _extract_number(price_tag.get_text()) if price_tag else None

    return PriceResult(
        price=price,
    )