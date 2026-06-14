"""Card manifest: load and validate ``og-manifest.json``.

The manifest is the per-build content contract. Any static-site generator can
emit it; ogcards never parses the generator's own files. This is what keeps the
tool framework-agnostic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ogcards.errors import ManifestError


@dataclass(frozen=True)
class Card:
    """One card to render. ``out`` is a path relative to the build's out-dir."""

    title: str
    out: str
    subtitle: str | None = None
    template: str = "post"


@dataclass(frozen=True)
class Manifest:
    """The full set of cards declared for a build."""

    cards: list[Card]


def load_manifest(path: Path) -> Manifest:
    """Parse and validate a manifest, raising :class:`ManifestError` on any fault."""
    if not path.is_file():
        raise ManifestError(f"manifest not found: {path}")
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(raw, dict) or "cards" not in raw:
        raise ManifestError("manifest must be an object with a 'cards' array")
    cards = raw["cards"]
    if not isinstance(cards, list):
        raise ManifestError("'cards' must be an array")
    return Manifest(cards=[_card(i, c) for i, c in enumerate(cards)])


def _card(index: int, d: Any) -> Card:
    if not isinstance(d, dict):
        raise ManifestError(f"cards[{index}] must be an object")
    title = d.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ManifestError(f"cards[{index}].title is required and must be a non-empty string")
    out = d.get("out")
    if not isinstance(out, str) or not out.strip():
        raise ManifestError(f"cards[{index}].out is required and must be a non-empty string")
    subtitle = d.get("subtitle")
    if subtitle is not None and not isinstance(subtitle, str):
        raise ManifestError(f"cards[{index}].subtitle must be a string")
    template = d.get("template", "post")
    if not isinstance(template, str):
        raise ManifestError(f"cards[{index}].template must be a string")
    return Card(title=title, out=out, subtitle=subtitle, template=template)
