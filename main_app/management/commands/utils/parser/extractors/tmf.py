from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:
    soup = BeautifulSoup(html, "lxml")

    # Карточка конкретной модели: <div class="b_form ..."><div class="price"><p>...</p>
    price_node = soup.select_one(".b_form.counter_wrapp .price > p")

    # Товар с вариантами: «от <цена>».
    if not price_node:
        price_node = soup.select_one(
            ".right_info.right .main-inf p.price span i:not(.dollar)"
        )

    price = _extract_number(price_node.get_text()) if price_node else None
    if price is None:
        return None

    return PriceResult(price=price)
