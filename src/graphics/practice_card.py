"""Compone la tarjeta de práctica: diagramas de la progresión + rasgueo + BPM."""

from PIL import Image, ImageDraw, ImageFont

from .chord_diagram import draw_chord_diagram

_PADDING = 20
_HEADER_HEIGHT = 70
_STRUM_ROW_HEIGHT = 70
_GAP_BETWEEN_DIAGRAMS = 14

_ARROW = {"D": "↓", "U": "↑", "-": "·"}


def _load_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def build_practice_card(
    chords: list[str],
    bpm: int,
    strum_name: str,
    strum_pattern: list[str],
    title: str = "Tarjeta de práctica",
) -> Image.Image:
    diagrams = [draw_chord_diagram(c) for c in chords]
    diagram_w = max(d.width for d in diagrams)
    diagram_h = max(d.height for d in diagrams)

    width = _PADDING * 2 + diagram_w * len(diagrams) + _GAP_BETWEEN_DIAGRAMS * (len(diagrams) - 1)
    height = _PADDING * 2 + _HEADER_HEIGHT + diagram_h + _STRUM_ROW_HEIGHT

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_title = _load_font(28)
    font_sub = _load_font(20, bold=False)
    font_arrow = _load_font(30)
    font_label = _load_font(16, bold=False)

    draw.text((width / 2, _PADDING), title, font=font_title, fill="black", anchor="ma")
    draw.text(
        (width / 2, _PADDING + 36),
        f"{bpm} BPM  ·  Rasgueo: {strum_name}",
        font=font_sub, fill="black", anchor="ma",
    )

    y_diagrams = _PADDING + _HEADER_HEIGHT
    x = _PADDING
    for diagram in diagrams:
        img.paste(diagram, (x, y_diagrams))
        x += diagram_w + _GAP_BETWEEN_DIAGRAMS

    y_strum = y_diagrams + diagram_h + 16
    draw.text((_PADDING, y_strum), "Patrón:", font=font_label, fill="black", anchor="lm")

    arrow_area_left = _PADDING + 70
    arrow_area_width = width - arrow_area_left - _PADDING
    step = arrow_area_width / max(len(strum_pattern), 1)
    for i, hit in enumerate(strum_pattern):
        cx = arrow_area_left + step * i + step / 2
        draw.text((cx, y_strum), _ARROW.get(hit, "?"), font=font_arrow, fill="black", anchor="mm")

    draw.text(
        (width / 2, height - _PADDING),
        "repite el patrón una vez por cada acorde",
        font=font_label, fill="gray", anchor="ms",
    )

    return img
