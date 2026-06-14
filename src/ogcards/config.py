"""Theme config: load and validate ``ogcards.toml`` into typed dataclasses.

The theme carries branding and is static across a build. It is deliberately
separate from the manifest (the per-build content). See ``manifest.py``.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ogcards.errors import ConfigError

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


@dataclass(frozen=True)
class Canvas:
    """Card dimensions, background, and an optional inset panel."""

    width: int = 1200
    height: int = 630
    background: str = "#ffffff"
    panel_background: str | None = None
    panel_border: str | None = None
    panel_inset: int = 32
    panel_radius: int = 16


@dataclass(frozen=True)
class Fonts:
    """Optional font overrides. When unset, the renderer resolves a default."""

    title: str | None = None
    meta: str | None = None


@dataclass(frozen=True)
class Template:
    """A named visual style. ``card.template`` selects one of these by name."""

    layout: str = "stack"
    title_size: int = 64
    title_color: str = "#1a1a1a"
    meta_size: int = 28
    meta_color: str = "#535358"
    accent: str = "#0645ad"
    padding: int = 80
    max_title_lines: int = 3
    line_spacing: float = 1.15


@dataclass(frozen=True)
class Theme:
    """The fully resolved theme: canvas, fonts, and named templates."""

    canvas: Canvas = field(default_factory=Canvas)
    fonts: Fonts = field(default_factory=Fonts)
    templates: dict[str, Template] = field(default_factory=lambda: {"post": Template()})

    def template(self, name: str) -> Template:
        """Look up a template, falling back to ``post`` then to defaults."""
        return self.templates.get(name) or self.templates.get("post") or Template()


def load_theme(path: Path) -> Theme:
    """Parse and validate a theme file, raising :class:`ConfigError` on any fault."""
    if not path.is_file():
        raise ConfigError(f"config not found: {path}")
    try:
        raw: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid TOML in {path}: {exc}") from exc

    templates_raw = raw.get("templates", {})
    if not isinstance(templates_raw, dict):
        raise ConfigError("[templates] must be a table")
    templates = {name: _template(name, body) for name, body in templates_raw.items()}
    templates.setdefault("post", Template())

    return Theme(
        canvas=_canvas(raw.get("canvas", {})),
        fonts=_fonts(raw.get("fonts", {})),
        templates=templates,
    )


def _canvas(d: dict[str, Any]) -> Canvas:
    return Canvas(
        width=_pos_int(d.get("width", 1200), "canvas.width"),
        height=_pos_int(d.get("height", 630), "canvas.height"),
        background=_color(d.get("background", "#ffffff"), "canvas.background"),
        panel_background=_opt_color(d.get("panel_background"), "canvas.panel_background"),
        panel_border=_opt_color(d.get("panel_border"), "canvas.panel_border"),
        panel_inset=_pos_int(d.get("panel_inset", 32), "canvas.panel_inset"),
        panel_radius=_pos_int(d.get("panel_radius", 16), "canvas.panel_radius"),
    )


def _fonts(d: dict[str, Any]) -> Fonts:
    for value, where in ((d.get("title"), "fonts.title"), (d.get("meta"), "fonts.meta")):
        if value is not None and not isinstance(value, str):
            raise ConfigError(f"{where}: expected a path string, got {value!r}")
    return Fonts(title=d.get("title"), meta=d.get("meta"))


def _template(name: str, d: Any) -> Template:
    if not isinstance(d, dict):
        raise ConfigError(f"[templates.{name}] must be a table")
    base = Template()
    return Template(
        layout=str(d.get("layout", base.layout)),
        title_size=_pos_int(d.get("title_size", base.title_size), f"templates.{name}.title_size"),
        title_color=_color(d.get("title_color", base.title_color), f"templates.{name}.title_color"),
        meta_size=_pos_int(d.get("meta_size", base.meta_size), f"templates.{name}.meta_size"),
        meta_color=_color(d.get("meta_color", base.meta_color), f"templates.{name}.meta_color"),
        accent=_color(d.get("accent", base.accent), f"templates.{name}.accent"),
        padding=_pos_int(d.get("padding", base.padding), f"templates.{name}.padding"),
        max_title_lines=_pos_int(
            d.get("max_title_lines", base.max_title_lines), f"templates.{name}.max_title_lines"
        ),
        line_spacing=_pos_float(
            d.get("line_spacing", base.line_spacing), f"templates.{name}.line_spacing"
        ),
    )


def _color(value: Any, where: str) -> str:
    if not isinstance(value, str) or not _HEX.match(value):
        raise ConfigError(f"{where}: expected a #RRGGBB hex color, got {value!r}")
    return value


def _opt_color(value: Any, where: str) -> str | None:
    return None if value is None else _color(value, where)


def _pos_int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigError(f"{where}: expected a positive integer, got {value!r}")
    return value


def _pos_float(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ConfigError(f"{where}: expected a positive number, got {value!r}")
    return float(value)
