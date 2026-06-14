"""Pillow rendering: font resolution, title wrapping, auto-fit, and the
built-in ``stack`` layout (title top, accent bar + subtitle bottom)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ogcards import templates
from ogcards.config import Template, Theme
from ogcards.errors import RenderError
from ogcards.manifest import Card

# Until a font is bundled (see fonts/README.md), fall back to system DejaVu so
# the tool works out of the box on Linux CI runners and dev machines.
_BUNDLED = Path(__file__).parent / "fonts"
_SYSTEM_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
_SYSTEM_REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def render_card(card: Card, template: Template, theme: Theme) -> Image.Image:
    """Render a single card to an in-memory image."""
    image = Image.new(
        "RGB",
        (theme.canvas.width, theme.canvas.height),
        _hex_to_rgb(theme.canvas.background),
    )
    draw = ImageDraw.Draw(image)
    templates.get_layout(template.layout)(image, draw, card, template, theme)
    return image


def _stack_layout(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    card: Card,
    template: Template,
    theme: Theme,
) -> None:
    width, height = theme.canvas.width, theme.canvas.height
    pad = template.padding
    max_width = width - 2 * pad

    title_font, lines = _fit_title(card.title, _title_font(theme), template, max_width)
    line_height = int(title_font.size * template.line_spacing)

    y = pad
    title_rgb = _hex_to_rgb(template.title_color)
    for line in lines:
        draw.text((pad, y), line, font=title_font, fill=title_rgb)
        y += line_height

    accent_rgb = _hex_to_rgb(template.accent)
    if card.subtitle:
        meta_font = ImageFont.truetype(str(_meta_font(theme)), template.meta_size)
        text_top = height - pad - template.meta_size
        bar_w, bar_h = 48, 6
        bar_y = text_top + (template.meta_size - bar_h) // 2
        draw.rectangle((pad, bar_y, pad + bar_w, bar_y + bar_h), fill=accent_rgb)
        draw.text(
            (pad + bar_w + 16, text_top),
            card.subtitle,
            font=meta_font,
            fill=_hex_to_rgb(template.meta_color),
        )
    else:
        draw.rectangle((pad, y + 8, pad + 96, y + 14), fill=accent_rgb)


def _fit_title(
    text: str,
    font_path: Path,
    template: Template,
    max_width: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Shrink the title font until it wraps within ``max_title_lines``."""
    size = template.title_size
    min_size = max(32, template.title_size // 2)
    font = ImageFont.truetype(str(font_path), size)
    lines = _wrap(text, font, max_width)
    while len(lines) > template.max_title_lines and size > min_size:
        size -= 4
        font = ImageFont.truetype(str(font_path), size)
        lines = _wrap(text, font, max_width)
    if len(lines) > template.max_title_lines:
        lines = lines[: template.max_title_lines]
        lines[-1] = _ellipsize(lines[-1], font, max_width)
    return font, lines


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.getlength(trial) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _ellipsize(line: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    ellipsis = "…"
    while line and font.getlength(line + ellipsis) > max_width:
        line = line[:-1].rstrip()
    return line + ellipsis


def _title_font(theme: Theme) -> Path:
    return _resolve_font(theme.fonts.title, "Inter-Bold.ttf", _SYSTEM_BOLD)


def _meta_font(theme: Theme) -> Path:
    return _resolve_font(theme.fonts.meta, "Inter-Regular.ttf", _SYSTEM_REGULAR)


def _resolve_font(explicit: str | None, bundled: str, system: Path) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.append(_BUNDLED / bundled)
    candidates.append(system)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    tried = ", ".join(str(c) for c in candidates)
    raise RenderError(f"no usable font found; set [fonts] in your config. tried: {tried}")


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))


templates.register("stack", _stack_layout)
