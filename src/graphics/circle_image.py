"""Genera la imagen de referencia del círculo de quintas (mayores + relativas menores)."""

import math
import os

from PIL import Image, ImageDraw, ImageFont

from ..theory.circle import CIRCLE_MAJOR_ORDER, RELATIVE_MINOR

_SIZE = 900
_CENTER = _SIZE // 2
_OUTER_R = 420
_MID_R = 320
_DIVIDER_R = 220
_INNER_R = 90
_STEP_DEG = 30  # 360 / 12


def _load_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def _point(radius: float, angle_deg: float) -> tuple[float, float]:
    angle = math.radians(angle_deg - 90)  # -90 para que la posición 0 quede arriba
    return (_CENTER + radius * math.cos(angle), _CENTER + radius * math.sin(angle))


def generate_circle_image() -> Image.Image:
    img = Image.new("RGB", (_SIZE, _SIZE), "white")
    draw = ImageDraw.Draw(img)

    font_major = _load_font(30)
    font_minor = _load_font(22, bold=False)
    font_title = _load_font(34)

    draw.ellipse(
        [_CENTER - _OUTER_R, _CENTER - _OUTER_R, _CENTER + _OUTER_R, _CENTER + _OUTER_R],
        outline="black", width=4,
    )
    draw.ellipse(
        [_CENTER - _DIVIDER_R, _CENTER - _DIVIDER_R, _CENTER + _DIVIDER_R, _CENTER + _DIVIDER_R],
        outline="black", width=2,
    )
    draw.ellipse(
        [_CENTER - _INNER_R, _CENTER - _INNER_R, _CENTER + _INNER_R, _CENTER + _INNER_R],
        outline="black", width=2,
    )

    for i in range(12):
        angle = i * _STEP_DEG - _STEP_DEG / 2
        x1, y1 = _point(_INNER_R, angle)
        x2, y2 = _point(_OUTER_R, angle)
        draw.line([(x1, y1), (x2, y2)], fill="gray", width=1)

    for i, (major, minor) in enumerate(zip(CIRCLE_MAJOR_ORDER, RELATIVE_MINOR)):
        angle = i * _STEP_DEG
        mx, my = _point(_MID_R, angle)
        draw.text((mx, my), major, font=font_major, fill="black", anchor="mm")
        ix, iy = _point((_DIVIDER_R + _INNER_R) / 2, angle)
        draw.text((ix, iy), minor, font=font_minor, fill="black", anchor="mm")

    draw.text((_CENTER, _CENTER), "Trivilín\nte guía", font=font_minor, fill="black", anchor="mm", align="center")
    draw.text((_CENTER, 30), "Círculo de Quintas", font=font_title, fill="black", anchor="ma")
    draw.text((_CENTER, _SIZE - 34), "afuera = mayores  ·  adentro = relativas menores",
               font=font_minor, fill="black", anchor="ma")

    return img


def get_or_create_circle_image(assets_dir: str) -> str:
    """Devuelve la ruta a la imagen cacheada, generándola si no existe."""
    os.makedirs(assets_dir, exist_ok=True)
    path = os.path.join(assets_dir, "circulo_quintas.png")
    if not os.path.exists(path):
        generate_circle_image().save(path)
    return path
