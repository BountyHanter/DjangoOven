PINNED_MANUFACTURER_NAME = "Печи Мельника"


def _manufacturer_group(name: str) -> int:
    normalized = (name or "").lstrip()

    if not normalized:
        return 3

    first_char = normalized[0]
    lower_char = first_char.lower()

    if first_char.isdigit():
        return 0

    if "a" <= lower_char <= "z":
        return 1

    if ("а" <= lower_char <= "я") or lower_char == "ё":
        return 2

    return 3


def manufacturer_sort_key(manufacturer):
    name = manufacturer.name or ""

    return (
        0 if name.casefold() == PINNED_MANUFACTURER_NAME.casefold() else 1,
        _manufacturer_group(name),
        name.casefold(),
        manufacturer.id,
    )


def sort_manufacturers(manufacturers):
    return sorted(manufacturers, key=manufacturer_sort_key)
