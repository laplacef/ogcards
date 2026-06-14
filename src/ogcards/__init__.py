"""ogcards — build-time Open Graph card generator for any static site."""

from __future__ import annotations

from ogcards.config import Theme, load_theme
from ogcards.manifest import Card, Manifest, load_manifest
from ogcards.render import render_card

__all__ = [
    "Card",
    "Manifest",
    "Theme",
    "load_manifest",
    "load_theme",
    "render_card",
]
__version__ = "0.1.0"
