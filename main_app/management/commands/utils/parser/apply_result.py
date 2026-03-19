from django.utils import timezone

from main_app.management.commands.utils.parser.schemas import FetchResult
from main_app.models.parser import ParserResult


def apply_parser_result(
    parser: ParserResult,
    fetch_result: FetchResult,
) -> None:
    product = parser.product
    data = fetch_result.data

    # --- статус и ошибка ---
    parser.status = fetch_result.status_code
    parser.error_text = fetch_result.error_text
    parser.processing_time = timezone.now()

    if data:
        # --- цены ---
        if data.old_price:
            product.price = int(data.old_price)
            product.discount_price = int(data.price) if data.price else None
        elif data.price:
            product.price = int(data.price)
            product.discount_price = None

        # --- наличие ---
        if data.in_stock is not None:
            product.in_stock = data.in_stock

        # --- активность ---
        if data.is_active is not None:
            product.is_active = data.is_active

    product.save(update_fields=[
        "price",
        "discount_price",
        "in_stock",
        "is_active",
        "updated_at",
    ])

    parser.save(update_fields=[
        "status",
        "error_text",
        "processing_time",
    ])