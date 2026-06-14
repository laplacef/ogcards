"""Layout registry. A layout draws a card onto a Pillow image.

Built-in layouts register themselves on import of :mod:`ogcards.render`. Third
parties can add their own with :func:`register` without forking the package.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ogcards.errors import RenderError

if TYPE_CHECKING:
    from PIL import Image, ImageDraw

    from ogcards.config import Template, Theme
    from ogcards.manifest import Card

Layout = Callable[
    ["Image.Image", "ImageDraw.ImageDraw", "Card", "Template", "Theme"],
    None,
]

_LAYOUTS: dict[str, Layout] = {}


def register(name: str, fn: Layout) -> None:
    """Register a layout under ``name`` (overwrites any existing one)."""
    _LAYOUTS[name] = fn


def get_layout(name: str) -> Layout:
    """Return the layout registered under ``name`` or raise :class:`RenderError`."""
    try:
        return _LAYOUTS[name]
    except KeyError:
        raise RenderError(f"unknown layout {name!r}; registered: {sorted(_LAYOUTS)}") from None
