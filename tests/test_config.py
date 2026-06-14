from __future__ import annotations

from pathlib import Path

import pytest

from ogcards.config import load_theme
from ogcards.errors import ConfigError


def test_load_valid(tmp_path: Path) -> None:
    path = tmp_path / "ogcards.toml"
    path.write_text('[canvas]\nwidth = 800\n[templates.post]\naccent = "#0645ad"\n')
    theme = load_theme(path)
    assert theme.canvas.width == 800
    assert theme.template("post").accent == "#0645ad"


def test_unknown_template_falls_back_to_post(tmp_path: Path) -> None:
    path = tmp_path / "ogcards.toml"
    path.write_text('[templates.post]\ntitle_size = 50\n')
    theme = load_theme(path)
    assert theme.template("nope").title_size == 50


def test_rejects_bad_color(tmp_path: Path) -> None:
    path = tmp_path / "ogcards.toml"
    path.write_text('[templates.post]\naccent = "blue"\n')
    with pytest.raises(ConfigError):
        load_theme(path)


def test_rejects_negative_size(tmp_path: Path) -> None:
    path = tmp_path / "ogcards.toml"
    path.write_text('[canvas]\nwidth = -5\n')
    with pytest.raises(ConfigError):
        load_theme(path)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_theme(tmp_path / "nope.toml")
