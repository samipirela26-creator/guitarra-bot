"""Compone una fila de diagramas de acordes con una etiqueta debajo de cada uno
(usado por /circulo para mostrar los 7 acordes diatónicos de una tonalidad)."""

from PIL import Image, ImageDraw, ImageFont

from .chord_diagram import draw_chord_diagram

_PADDING = 20
_HEADER_HEIGHT = 40
_LABEL_ROW_HEIGHT = 30
_GAP_BETWEEN_DIAGRAMS = 14


def _load_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def build_chord_row(chords: list[str], labels: list[str], title: str = "") -> Image.Image:
    """Dibuja los diagramas de `chords` en fila, con `labels` (mismo largo,
    p. ej. los numerales romanos I, ii, iii...) centrados debajo de cada uno."""
    diagrams = [draw_chord_diagram(c) for c in chords]
    diagram_w = max(d.width for d in diagrams)
    diagram_h = max(d.height for d in diagrams)

    width = _PADDING * 2 + diagram_w * len(diagrams) + _GAP_BETWEEN_DIAGRAMS * (len(diagrams) - 1)
    header_h = _HEADER_HEIGHT if title else 0
    height = _PADDING * 2 + header_h + diagram_h + _LABEL_ROW_HEIGHT

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_title = _load_font(24)
    font_label = _load_font(18, bold=False)

    if title:
        draw.text((width / 2, _PADDING), title, font=font_title, fill="black", anchor="ma")

    y_diagrams = _PADDING + header_h
    x = _PADDING
    for diagram, label in zip(diagrams, labels):
        img.paste(diagram, (x, y_diagrams))
        cx = x + diagram_w / 2
        draw.text((cx, y_diagrams + diagram_h + 6), label, font=font_label, fill="black", anchor="ma")
        x += diagram_w + _GAP_BETWEEN_DIAGRAMS

    return img
