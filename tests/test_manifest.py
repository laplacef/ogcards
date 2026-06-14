from __future__ import annotations

from pathlib import Path

import pytest

from ogcards.errors import ManifestError
from ogcards.manifest import load_manifest


def test_load_valid(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text('{"cards":[{"title":"A","out":"a.png"}]}')
    manifest = load_manifest(path)
    assert len(manifest.cards) == 1
    assert manifest.cards[0].template == "post"
    assert manifest.cards[0].subtitle is None


def test_rejects_missing_title(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text('{"cards":[{"out":"a.png"}]}')
    with pytest.raises(ManifestError):
        load_manifest(path)


def test_rejects_non_object_root(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text("[]")
    with pytest.raises(ManifestError):
        load_manifest(path)
