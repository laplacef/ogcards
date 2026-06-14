from __future__ import annotations

from PIL import ImageFont

from ogcards.config import Theme
from ogcards.manifest import Card
from ogcards.render import _wrap, render_card


def test_dimensions_and_mode() -> None:
    theme = Theme()
    card = Card(title="Hello World", out="x.png", subtitle="June 2026")
    image = render_card(card, theme.template("post"), theme)
    assert image.size == (1200, 630)
    assert image.mode == "RGB"


def test_renders_non_blank_canvas() -> None:
    theme = Theme()
    card = Card(title="Hello", out="x.png", subtitle="June 2026")
    image = render_card(card, theme.template("post"), theme)
    colors = image.getcolors(maxcolors=200_000)
    assert colors is not None
    assert len(colors) > 1  # more than just the background


def test_wrap_breaks_long_text() -> None:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
    lines = _wrap("one two three four five six seven eight nine ten", font, 300)
    assert len(lines) > 1
    assert all(line for line in lines)
