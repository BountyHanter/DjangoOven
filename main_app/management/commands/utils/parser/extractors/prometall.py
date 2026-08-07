from bs4 import BeautifulSoup

from main_app.management.commands.utils.parser.extract_number import _extract_number
from main_app.management.commands.utils.parser.schemas import PriceResult


def extract_price(html: str) -> PriceResult | None:

    soup = BeautifulSoup(html, "lxml")

    product = soup.select_one(".js-product-single, .t744__textwrapper")
    if not product:
        return None

    price = None
    old_price = None

    # ---- цена ----
    price_node = product.select_one(
        ".js-product-price, .js-store-prod-price-val"
    )

    if price_node:
        price = _extract_number(
            price_node.get("data-product-price-def") or price_node.get_text()
        )

    # ---- старая цена ----
    old_price_node = product.select_one(".js-store-prod-price-old-val")

    if old_price_node:
        old_price = _extract_number(old_price_node.get_text())

    # Tilda: disabled button with the text "Out of stock" means no stock.
    buy_button = product.select_one(".t744__btn")
    in_stock = None
    if buy_button:
        button_text = buy_button.get_text(" ", strip=True).lower()
        button_classes = buy_button.get("class", [])

        if (
            "t-store__prod-popup__btn_disabled" in button_classes
            or "out of stock" in button_text
        ):
            in_stock = False
        elif "купить" in button_text:
            in_stock = True

    if price is None and old_price is None and in_stock is None:
        return None

    return PriceResult(
        price=price,
        old_price=old_price,
        in_stock=in_stock,
    )
