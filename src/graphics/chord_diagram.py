"""Dibuja un diagrama de acorde (mástil en miniatura) con Pillow."""

from PIL import Image, ImageDraw, ImageFont

from ..theory.chord_shapes import resolve_diagram

_STRINGS = 6
_FRETS_SHOWN = 4
_MARGIN_TOP = 34  # espacio para indicadores x/o y el nombre del acorde
_MARGIN_LEFT = 30  # espacio extra para la etiqueta "Nfr"
_MARGIN_RIGHT = 14
_MARGIN_BOTTOM = 10
_NOTE_HEIGHT = 16  # espacio extra abajo cuando hay una nota aclaratoria (aproximación)
_FRET_HEIGHT = 34
_STRING_GAP = 22


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def draw_chord_diagram(chord_name: str) -> Image.Image:
    shape, note = resolve_diagram(chord_name)
    has_open_string = 0 in shape
    fretted = [f for f in shape if isinstance(f, int) and f > 0]
    # Los acordes con cuerdas al aire siempre son de posición abierta (empiezan en la cejilla/nut).
    # Solo las formas sin cuerdas al aire pueden ser de cejilla (barre) en un traste alto.
    start_fret = 1 if has_open_string else (min(fretted) if fretted else 1)

    width = _MARGIN_LEFT + _MARGIN_RIGHT + _STRING_GAP * (_STRINGS - 1)
    height = _MARGIN_TOP + _FRET_HEIGHT * _FRETS_SHOWN + _MARGIN_BOTTOM
    if note:
        height += _NOTE_HEIGHT
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_small = _load_font(15)
    title_size = 20 if len(chord_name) <= 2 else (16 if len(chord_name) <= 4 else 13)
    font_title = _load_font(title_size)

    draw.text((width / 2, 2), chord_name, font=font_title, fill="black", anchor="ma")

    board_top = _MARGIN_TOP
    board_left = _MARGIN_LEFT
    board_right = width - _MARGIN_RIGHT

    if start_fret == 1:
        draw.line([(board_left, board_top), (board_right, board_top)], fill="black", width=5)
    else:
        draw.line([(board_left, board_top), (board_right, board_top)], fill="black", width=2)
        draw.text((board_left - 6, board_top + _FRET_HEIGHT / 2), f"{start_fret}fr",
                   font=font_small, fill="black", anchor="rm")

    for i in range(1, _FRETS_SHOWN + 1):
        y = board_top + i * _FRET_HEIGHT
        draw.line([(board_left, y), (board_right, y)], fill="gray", width=1)

    for s in range(_STRINGS):
        x = board_left + s * _STRING_GAP
        draw.line([(x, board_top), (x, board_top + _FRET_HEIGHT * _FRETS_SHOWN)], fill="black", width=1)

    # Indicadores x/o encima de la cejilla
    for s, fret in enumerate(shape):
        x = board_left + s * _STRING_GAP
        if fret == "x":
            draw.text((x, board_top - 22), "x", font=font_small, fill="black", anchor="ma")
        elif fret == 0:
            draw.text((x, board_top - 22), "o", font=font_small, fill="black", anchor="ma")

    # Cejilla (barra): el dedo índice pisa desde la primera hasta la última cuerda
    # NO apagada que están en el traste más bajo (start_fret).
    fretted_indices = [s for s, f in enumerate(shape) if isinstance(f, int) and f > 0]
    barre_range = None
    if fretted_indices and not has_open_string:
        lo, hi = fretted_indices[0], fretted_indices[-1]
        if hi - lo >= 2 and shape[lo] == start_fret and shape[hi] == start_fret:
            barre_range = (lo, hi)
            y = board_top + _FRET_HEIGHT / 2
            x1 = board_left + lo * _STRING_GAP
            x2 = board_left + hi * _STRING_GAP
            draw.line([(x1, y), (x2, y)], fill="black", width=12)

    # Puntos de dedos (se omiten en los extremos ya cubiertos por la barra)
    for s, fret in enumerate(shape):
        if not (isinstance(fret, int) and fret > 0):
            continue
        if barre_range and fret == start_fret and barre_range[0] <= s <= barre_range[1]:
            continue
        rel_fret = fret - start_fret + 1
        if 1 <= rel_fret <= _FRETS_SHOWN:
            x = board_left + s * _STRING_GAP
            y = board_top + (rel_fret - 1) * _FRET_HEIGHT + _FRET_HEIGHT / 2
            r = 8
            draw.ellipse([x - r, y - r, x + r, y + r], fill="black")

    if note:
        font_note = _load_font(11)
        note_y = board_top + _FRET_HEIGHT * _FRETS_SHOWN + 4
        draw.text((width / 2, note_y), note, font=font_note, fill="gray", anchor="ma")

    return img
