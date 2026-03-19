from dataclasses import dataclass


@dataclass(slots=True)
class PriceResult:
    price: float | None = None
    old_price: float | None = None
    in_stock: bool | None = None
    is_active: bool | None = None


@dataclass(slots=True)
class FetchResult:
    status_code: int | None = None
    data: PriceResult | None = None
    error_text: str | None = None

    def __repr__(self):
        return (
            f"FetchResult("
            f"status_code={self.status_code}, "
            f"data={self.data}, "
            f"error_text={self.error_text}"
            f")"
        )
