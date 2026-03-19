from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.schemas import PriceResult
from main_app.management.commands.utils.parser.extract_number import _extract_number


def extract_price(html: str) -> PriceResult:
    result = PriceResult()

    soup = BeautifulSoup(html, "lxml")

    aside = soup.select_one("aside")
    if not aside:
        result.in_stock = False
        return result

    # ---- статус ----
    status_block = aside.select_one(".mb-2.caption-accent")
    if status_block:
        status_text = " ".join(status_block.stripped_strings).lower()

        if "снят с производства" in status_text:
            result.in_stock = False
            result.is_active = False
            return result

        if "под заказ" in status_text:
            result.in_stock = False
        elif "в наличии" in status_text:
            result.in_stock = True
        else:
            result.in_stock = False
    else:
        result.in_stock = False

    # ---- цена ----
    price_node = aside.select_one("strong.headline-small")
    if price_node:
        result.price = _extract_number("".join(price_node.stripped_strings))

    # ---- старая цена ----
    old_price_node = aside.select_one("span.title-medium")
    if old_price_node:
        result.old_price = _extract_number("".join(old_price_node.stripped_strings))

    return result