"""Patrones de rasgueo y tiempos sugeridos para las tarjetas de práctica.

Los patrones están tomados de esquemas de rasgueo reales de método de guitarra
(p. ej. "Guitarra para Dummies", capítulo de rasgueo con acordes abiertos:
Figura 4-2 "cuatro rasgueos descendentes por acorde", Figura 4-4 "abajo,
abajo-arriba, abajo, abajo", Figura 4-6 "tiempos 2 y 3 en abajo-arriba" y
Figura 4-8 "esquema sincopado, sin golpe en el tiempo 3" — el efecto sincopado
"le da a la canción un aire latino", según el propio libro). Cada patrón
representa UN compás de 4/4 dividido en corcheas (8 corcheas = 8 símbolos) o
en negras (4 símbolos), y se repite igual bajo cada acorde de la progresión
(un compás por acorde, como enseña el libro).
"""

import random

# Cada patrón es una secuencia de golpes por compás: 'D' = abajo, 'U' = arriba, '-' = silencio/no tocar.
STRUM_PATTERNS = [
    ("Básico", ["D", "D", "D", "D"]),
    ("Popular", ["D", "D", "U", "U", "D", "U"]),
    ("Balada", ["D", "-", "D", "U", "-", "U", "D", "U"]),
    ("Contratiempo", ["-", "U", "-", "U", "-", "U", "-", "U"]),
    # Figura 4-4 del libro: "abajo, abajo-arriba, abajo, abajo".
    ("Country", ["D", "-", "D", "U", "D", "-", "D", "-"]),
    # Figura 4-8 del libro: sin golpe en el tiempo 3 (síncopa con aire latino).
    ("Sincopado", ["D", "-", "D", "U", "-", "-", "D", "-"]),
    # Shuffle de blues: corcheas "swing" en pares abajo-arriba con acento.
    ("Shuffle", ["D", "-", "D", "U", "D", "-", "D", "U"]),
    # Comping de jazz: golpes cortos en tiempos débiles, espacioso.
    ("Jazz", ["-", "D", "-", "D", "-", "D", "-", "D"]),
]

# Qué patrones de rasgueo le quedan bien a cada estilo de /tarjeta (ver
# theory.progressions.STYLE_PROGRESSIONS). Se usa para no mezclar, por
# ejemplo, un rasgueo "Contratiempo" (reggae) con una progresión de Jazz.
STYLE_STRUM_NAMES: dict[str, list[str]] = {
    "Pop": ["Popular", "Básico", "Balada"],
    "Balada": ["Balada", "Básico"],
    "Rock": ["Básico", "Popular", "Country"],
    "Blues": ["Shuffle", "Básico"],
    "Jazz": ["Jazz"],
    "Reggae": ["Contratiempo"],
    "Bachata": ["Sincopado"],
    "Adoración": ["Balada", "Popular", "Sincopado"],
}

_BPM_CHOICES = list(range(60, 115, 5))


def random_strum_pattern(
    rng: random.Random | None = None, style: str | None = None
) -> tuple[str, list[str]]:
    """Elige un patrón de rasgueo al azar. Si se da `style` (uno de los
    estilos de STYLE_PROGRESSIONS), restringe la elección a los patrones que
    le quedan bien a ese estilo (ver STYLE_STRUM_NAMES)."""
    rng = rng or random
    pool = STRUM_PATTERNS
    if style is not None and style in STYLE_STRUM_NAMES:
        allowed = set(STYLE_STRUM_NAMES[style])
        pool = [p for p in STRUM_PATTERNS if p[0] in allowed]
    return rng.choice(pool)


def random_bpm(rng: random.Random | None = None) -> int:
    rng = rng or random
    return rng.choice(_BPM_CHOICES)
