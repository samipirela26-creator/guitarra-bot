"""Patrones de rasgueo y tiempos sugeridos para las tarjetas de práctica."""

import random

# Cada patrón es una secuencia de golpes por compás: 'D' = abajo, 'U' = arriba, '-' = silencio/no tocar.
STRUM_PATTERNS = [
    ("Básico", ["D", "D", "D", "D"]),
    ("Popular", ["D", "D", "U", "U", "D", "U"]),
    ("Balada", ["D", "-", "D", "U", "-", "U", "D", "U"]),
    ("Contratiempo", ["-", "U", "-", "U", "-", "U", "-", "U"]),
]

_BPM_CHOICES = list(range(60, 115, 5))


def random_strum_pattern(rng: random.Random | None = None) -> tuple[str, list[str]]:
    rng = rng or random
    return rng.choice(STRUM_PATTERNS)


def random_bpm(rng: random.Random | None = None) -> int:
    rng = rng or random
    return rng.choice(_BPM_CHOICES)
