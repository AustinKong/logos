import hashlib
from uuid import UUID

from textual.color import Color


def color_from_id(uuid: UUID, base_color_hex: str) -> Color:
    """Return a stable, hash-distributed color using the hue from the id and saturation/lightness from the base color."""
    hue = int(hashlib.sha256(str(uuid).encode("utf-8")).hexdigest(), 16) % 360 / 360.0

    base_color = Color.parse(base_color_hex)
    _, s, l = base_color.hsl

    return Color.from_hsl(hue, s, l)
