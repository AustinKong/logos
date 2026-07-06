from collections.abc import Iterable


def find_last_instance[T](
    items: Iterable[object],
    item_types: type[T] | tuple[type[T], ...],
) -> tuple[int, T] | None:
    """Return the index and item for the last value matching the provided type or types."""
    indexed_items = tuple(items)
    for index in range(len(indexed_items) - 1, -1, -1):
        item = indexed_items[index]
        if isinstance(item, item_types):
            return index, item

    return None
