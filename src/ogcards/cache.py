"""Incremental rendering: a card is re-rendered only when its inputs change.

The fingerprint folds in the card, its resolved template, and a theme token so
that a branding tweak (canvas size, fonts) invalidates every card.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from ogcards.config import Template
from ogcards.manifest import Card


def fingerprint(card: Card, template: Template, theme_token: str) -> str:
    """Return a stable hash of everything that affects a card's pixels."""
    payload = json.dumps(
        {"card": asdict(card), "template": asdict(template), "theme": theme_token},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_cache(path: Path) -> dict[str, str]:
    """Read the out-path -> fingerprint map, or an empty map if absent/corrupt."""
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def save_cache(path: Path, cache: dict[str, str]) -> None:
    """Persist the fingerprint map next to the rendered output."""
    path.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
