"""Pillow rendering: font resolution, title wrapping, auto-fit, and the
built-in ``stack`` layout (left accent rail, centered title, footer rule)."""

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
    bg = _hex_to_rgb(theme.canvas.background)
    accent = _hex_to_rgb(template.accent)
    title_rgb = _hex_to_rgb(template.title_color)
    meta_rgb = _hex_to_rgb(template.meta_color)
    inner_w = width - 2 * pad

    # Optional inset panel behind the content (e.g. a framed card on a dark bg).
    canvas = theme.canvas
    if canvas.panel_background:
        inset = canvas.panel_inset
        draw.rounded_rectangle(
            (inset, inset, width - inset, height - inset),
            radius=canvas.panel_radius,
            fill=_hex_to_rgb(canvas.panel_background),
            outline=_hex_to_rgb(canvas.panel_border) if canvas.panel_border else None,
            width=2,
        )

    # Kicker: a tracked, uppercase context label at the top.
    kicker_size = max(20, int(template.meta_size * 0.78))
    if card.kicker:
        kicker_font = ImageFont.truetype(str(_meta_font(theme)), kicker_size)
        _draw_tracked(draw, (pad, pad), card.kicker.upper(), kicker_font, accent, 5)
    band_top = pad + (kicker_size + 28 if card.kicker else 0)

    # Footer band (rule + brand left + label right) when there is footer content.
    has_footer = bool(card.footer or card.label)
    if has_footer:
        footer_y = height - pad - template.meta_size
        rule_y = footer_y - 30
        band_bottom = rule_y - 44
    else:
        band_bottom = height - pad

    # Title (auto-fit) + subtitle, vertically centered in the band between them.
    title_font, lines = _fit_title(card.title, _title_font(theme), template, inner_w)
    line_height = int(title_font.size * template.line_spacing)
    sub_gap = 18
    block_h = line_height * len(lines) + (template.meta_size + sub_gap if card.subtitle else 0)
    y = band_top + max(0, (band_bottom - band_top - block_h) // 2)
    for line in lines:
        draw.text((pad, y), line, font=title_font, fill=title_rgb)
        y += line_height
    if card.subtitle:
        sub_font = ImageFont.truetype(str(_meta_font(theme)), template.meta_size)
        draw.text((pad, y + sub_gap), card.subtitle, font=sub_font, fill=meta_rgb)

    if has_footer:
        draw.rectangle((pad, rule_y, width - pad, rule_y + 2), fill=_mix(bg, meta_rgb, 0.4))
        footer_font = ImageFont.truetype(str(_meta_font(theme)), template.meta_size)
        if card.footer:
            draw.text((pad, footer_y), card.footer, font=footer_font, fill=title_rgb)
        if card.label:
            label_w = footer_font.getlength(card.label)
            draw.text(
                (width - pad - label_w, footer_y),
                card.label,
                font=footer_font,
                fill=meta_rgb,
            )


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
        # A bare filename selects a bundled font; a path selects an explicit file.
        candidates.append(_BUNDLED / explicit if "/" not in explicit else Path(explicit))
    candidates.append(_BUNDLED / bundled)
    candidates.append(system)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    tried = ", ".join(str(c) for c in candidates)
    raise RenderError(f"no usable font found; set [fonts] in your config. tried: {tried}")


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))


def _draw_tracked(
    draw: ImageDraw.ImageDraw,
    pos: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    tracking: int,
) -> None:
    """Draw ``text`` with extra letter-spacing (manual tracking, char by char)."""
    x = float(pos[0])
    for char in text:
        draw.text((x, float(pos[1])), char, font=font, fill=fill)
        x += font.getlength(char) + tracking


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Linear blend of two RGB colors, ``t`` of the way from ``a`` toward ``b``."""
    return (
        round(a[0] * (1 - t) + b[0] * t),
        round(a[1] * (1 - t) + b[1] * t),
        round(a[2] * (1 - t) + b[2] * t),
    )


templates.register("stack", _stack_layout)
