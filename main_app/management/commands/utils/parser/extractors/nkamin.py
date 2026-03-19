from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:

    soup = BeautifulSoup(html, "lxml")

    card = soup.select_one(".card_data_left")
    if not card:
        return None

    # ---- цена ----
    price_node = card.select_one(".price_formatted")
    old_price_node = card.select_one(".price_old em")

    price = None
    old_price = None

    if price_node:
        price = _extract_number(price_node.get_text())

    if old_price_node:
        old_price = _extract_number(old_price_node.get_text())

    if price is None and old_price is None:
        return None

    # ---- наличие ----
    stock = False
    is_active = False

    info = soup.select_one(".card_data_info")
    if info:

        text = " ".join(info.stripped_strings).lower()

        # если есть в наличии
        if "в наличии" in text:
            stock = True
            is_active = True

        # ожидается считаем как наличие
        elif "ожидается" in text:
            stock = True
            is_active = True

        # наличие в магазинах
        elif "есть" in text and "магаз" in text:
            stock = True
            is_active = True

        # иначе False

    return PriceResult(
        price=price,
        old_price=old_price,
        in_stock=stock,
        is_active=is_active,
    )