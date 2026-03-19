import re


def _extract_number(text: str) -> float | None:
    if not text:
        return None

    cleaned = text.replace("\xa0", "").replace(" ", "").strip()
    m = re.search(r"\d+(?:[.,]\d+)?", cleaned)
    if not m:
        return None

    return float(m.group(0).replace(",", "."))
