"""Progresiones diatónicas comunes y generación de preguntas de transposición."""

import random

from .notes import NOTE_NAMES, format_chord, transpose_progression

MAJOR_SCALE_STEPS = [0, 2, 4, 5, 7, 9, 11]
# Calidad del acorde diatónico para cada grado (I..vii). '' = mayor.
DEGREE_QUALITY = ["", "m", "m", "", "", "m", "dim"]
# Numeral romano de cada grado, mismo índice que DEGREE_QUALITY/MAJOR_SCALE_STEPS.
DEGREE_ROMAN = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]

# Para qué sirve cada grado dentro de la tonalidad (función armónica), en términos
# simples — usado por /circulo cuando el usuario toca una tonalidad para ver su
# "círculo armónico" completo (los 7 acordes diatónicos con los que puede
# acompañar/componer en esa tonalidad).
DEGREE_FUNCTION = [
    "tónica: el acorde de \"casa\", ahí descansa la canción.",
    "subdominante suave: prepara el camino hacia la dominante (la cadencia ii-V-I).",
    "mediante: comparte notas con la tónica, la sustituye con un color más melancólico.",
    "subdominante: se aleja de la tónica, genera una tensión leve antes de ir a la dominante.",
    "dominante: la máxima tensión de la escala, empuja con fuerza a resolver en la tónica (I).",
    "relativa menor: mismas notas que la tónica pero en menor, funciona como una tónica alternativa y más triste.",
    "sensible: casi siempre resuelve rápido hacia la tónica (I), poco usado solo.",
]

# (nombre en números romanos, grados usados, para mostrar en la pregunta)
COMMON_PROGRESSIONS = [
    ("I - IV - V - I", [0, 3, 4, 0]),
    ("I - V - vi - IV", [0, 4, 5, 3]),
    ("I - vi - IV - V", [0, 5, 3, 4]),
    ("ii - V - I", [1, 4, 0]),
    ("I - IV - I - V", [0, 3, 0, 4]),
    ("vi - IV - I - V", [5, 3, 0, 4]),
]

# Por qué cada progresión "suena bien": la lógica de tensión/resolución detrás,
# explicada en términos simples (tónica = casa, dominante = tensión que pide volver).
PROGRESSION_EXPLANATIONS = {
    "I - IV - V - I": (
        "La progresión más básica de la armonía tonal: tónica (I, "
        "\"casa\") → subdominante (IV, se aleja) → dominante (V, "
        "máxima tensión) → tónica (I, resuelve). El V crea una nota "
        "sensible que \"pide\" volver al I, por eso el regreso se "
        "siente tan satisfactorio."
    ),
    "I - V - vi - IV": (
        "La \"progresión de 4 acordes\" que aparece en cientos de "
        "canciones pop. Va del I al V (tensión) pero en vez de resolver "
        "cae en vi (la relativa menor, mismo color pero más melancólico) "
        "y de ahí al IV — nunca vuelve a cerrar del todo en el I, así que "
        "el ciclo se siente natural para repetirlo sin cansar."
    ),
    "I - vi - IV - V": (
        "La progresión \"doo-wop\" de las baladas de los 50s-60s. "
        "Alterna la tónica (I) con su relativa menor (vi, mismas notas "
        "de la escala, ánimo más triste) antes de subir por la "
        "subdominante (IV) hacia la dominante (V), que empuja de vuelta "
        "al I para repetir el ciclo."
    ),
    "ii - V - I": (
        "La cadencia más importante del jazz (ii-V-I). El ii ya anticipa "
        "la dominante (comparte dos notas con el V), el V genera la "
        "tensión máxima (tiene la nota sensible que quiere subir a la "
        "tónica) y el I resuelve todo. Es el motor armónico detrás de "
        "casi cualquier estándar de jazz."
    ),
    "I - IV - I - V": (
        "Variante simple que refuerza la tónica (I) dos veces antes de "
        "moverse: primero un paseo corto a la subdominante (IV) y vuelta "
        "a casa, luego sí se anima a ir a la dominante (V), que deja la "
        "puerta abierta para repetir el ciclo."
    ),
    "vi - IV - I - V": (
        "La misma \"progresión de 4 acordes\" pop, pero arrancando desde "
        "la relativa menor (vi) en vez del I — mismos acordes, mismo "
        "ciclo de tensión y resolución, pero al empezar en menor suena "
        "más introspectiva antes de asentarse en la tónica (I) y salir "
        "hacia la dominante (V)."
    ),
}


def build_progression(key_root_pc: int, degrees: list[int]) -> list[str]:
    chords = []
    for degree in degrees:
        interval = MAJOR_SCALE_STEPS[degree]
        quality = DEGREE_QUALITY[degree]
        chords.append(format_chord(key_root_pc + interval, quality))
    return chords


def harmonic_circle(key_root_pc: int) -> list[tuple[str, str, str]]:
    """Los 7 acordes diatónicos de una tonalidad mayor, listos para mostrar en
    /circulo: [(numeral romano, acorde, para qué sirve), ...]."""
    chords = build_progression(key_root_pc, list(range(7)))
    return list(zip(DEGREE_ROMAN, chords, DEGREE_FUNCTION))


def build_progression_ext(key_root_pc: int, degree_qualities: list[tuple[int, str]]) -> list[str]:
    """Como build_progression, pero cada grado trae su propia calidad explícita
    (permite 7, maj7, m7, sus4 en vez de solo la tríada diatónica por defecto)."""
    chords = []
    for degree, quality in degree_qualities:
        interval = MAJOR_SCALE_STEPS[degree]
        chords.append(format_chord(key_root_pc + interval, quality))
    return chords


# Progresiones agrupadas por estilo musical, con calidades explícitas (no solo
# tríadas) para enriquecer las tarjetas de práctica (/tarjeta) más allá de los
# acordes básicos. Cada entrada: (nombre en números romanos, [(grado, calidad), ...]).
# Espacio combinatorio: 8 estilos × 8 progresiones × 12 tonalidades × 4 patrones
# de rasgueo (ver theory.rhythm.STRUM_PATTERNS) = 3072 tarjetas distintas posibles.
STYLE_PROGRESSIONS: dict[str, list[tuple[str, list[tuple[int, str]]]]] = {
    "Pop": [
        ("I - V - vi - IV", [(0, ""), (4, ""), (5, "m"), (3, "")]),
        ("vi - IV - I - V", [(5, "m"), (3, ""), (0, ""), (4, "")]),
        ("I - IV - V - I", [(0, ""), (3, ""), (4, ""), (0, "")]),
        ("I - vi - IV - V", [(0, ""), (5, "m"), (3, ""), (4, "")]),
        ("IV - I - V - vi", [(3, ""), (0, ""), (4, ""), (5, "m")]),
        ("I - V - IV - V", [(0, ""), (4, ""), (3, ""), (4, "")]),
        ("vi - V - IV - V", [(5, "m"), (4, ""), (3, ""), (4, "")]),
        ("I - IV - vi - V", [(0, ""), (3, ""), (5, "m"), (4, "")]),
    ],
    "Balada": [
        ("I - vi - IV - V", [(0, ""), (5, "m"), (3, ""), (4, "")]),
        ("I - iii - IV - V", [(0, ""), (2, "m"), (3, ""), (4, "")]),
        ("vi - IV - Vsus4 - V", [(5, "m"), (3, ""), (4, "sus4"), (4, "")]),
        ("I - IVmaj7 - V - vi", [(0, ""), (3, "maj7"), (4, ""), (5, "m")]),
        ("Imaj7 - vi - IV - V", [(0, "maj7"), (5, "m"), (3, ""), (4, "")]),
        ("ii - IV - Isus4 - I", [(1, "m"), (3, ""), (0, "sus4"), (0, "")]),
        ("I - V - vi - iii", [(0, ""), (4, ""), (5, "m"), (2, "m")]),
        ("IV - Vsus4 - V - I", [(3, ""), (4, "sus4"), (4, ""), (0, "")]),
    ],
    "Rock": [
        ("I - IV - V - IV", [(0, ""), (3, ""), (4, ""), (3, "")]),
        ("vi - IV - I - V", [(5, "m"), (3, ""), (0, ""), (4, "")]),
        ("I - V - IV - I", [(0, ""), (4, ""), (3, ""), (0, "")]),
        ("ii - IV - I - V", [(1, "m"), (3, ""), (0, ""), (4, "")]),
        ("I - IV - I - V", [(0, ""), (3, ""), (0, ""), (4, "")]),
        ("IV - V - I - vi", [(3, ""), (4, ""), (0, ""), (5, "m")]),
        ("I - vi - ii - V", [(0, ""), (5, "m"), (1, "m"), (4, "")]),
        ("vi - I - IV - V", [(5, "m"), (0, ""), (3, ""), (4, "")]),
    ],
    "Blues": [
        ("I7 - IV7 - I7 - V7", [(0, "7"), (3, "7"), (0, "7"), (4, "7")]),
        ("I7 - IV7 - V7 - IV7", [(0, "7"), (3, "7"), (4, "7"), (3, "7")]),
        ("I7 - I7 - IV7 - IV7", [(0, "7"), (0, "7"), (3, "7"), (3, "7")]),
        ("ii7 - V7 - I7 (turnaround)", [(1, "m7"), (4, "7"), (0, "7")]),
        ("I7 - IV7 - I7 - I7", [(0, "7"), (3, "7"), (0, "7"), (0, "7")]),
        ("V7 - IV7 - I7 - V7", [(4, "7"), (3, "7"), (0, "7"), (4, "7")]),
        ("I7 - vi7 - ii7 - V7", [(0, "7"), (5, "m7"), (1, "m7"), (4, "7")]),
        ("IV7 - I7 - V7 - I7", [(3, "7"), (0, "7"), (4, "7"), (0, "7")]),
    ],
    "Jazz": [
        ("ii7 - V7 - Imaj7", [(1, "m7"), (4, "7"), (0, "maj7")]),
        ("vi7 - ii7 - V7 - Imaj7", [(5, "m7"), (1, "m7"), (4, "7"), (0, "maj7")]),
        ("Imaj7 - vi7 - ii7 - V7", [(0, "maj7"), (5, "m7"), (1, "m7"), (4, "7")]),
        ("iii7 - vi7 - ii7 - V7", [(2, "m7"), (5, "m7"), (1, "m7"), (4, "7")]),
        ("IVmaj7 - V7 - iii7 - vi7", [(3, "maj7"), (4, "7"), (2, "m7"), (5, "m7")]),
        ("Imaj7 - IVmaj7 - iii7 - vi7", [(0, "maj7"), (3, "maj7"), (2, "m7"), (5, "m7")]),
        ("ii7 - V7 - vi7 - IVmaj7", [(1, "m7"), (4, "7"), (5, "m7"), (3, "maj7")]),
        ("Imaj7 - ii7 - iii7 - IVmaj7", [(0, "maj7"), (1, "m7"), (2, "m7"), (3, "maj7")]),
    ],
    "Reggae": [
        ("I - V - vi - IV", [(0, ""), (4, ""), (5, "m"), (3, "")]),
        ("vi - IV - V - I", [(5, "m"), (3, ""), (4, ""), (0, "")]),
        ("I - IV - I - V", [(0, ""), (3, ""), (0, ""), (4, "")]),
        ("ii - V - I - IV", [(1, "m"), (4, ""), (0, ""), (3, "")]),
        ("I - iii - IV - V", [(0, ""), (2, "m"), (3, ""), (4, "")]),
        ("vi - ii - V - I", [(5, "m"), (1, "m"), (4, ""), (0, "")]),
        ("IV - V - vi - I", [(3, ""), (4, ""), (5, "m"), (0, "")]),
        ("I - IVsus4 - IV - V", [(0, ""), (3, "sus4"), (3, ""), (4, "")]),
    ],
    "Bachata": [
        ("vi - IV - I - V", [(5, "m"), (3, ""), (0, ""), (4, "")]),
        ("vi - V - IV - V", [(5, "m"), (4, ""), (3, ""), (4, "")]),
        ("vi - IV - vi - V", [(5, "m"), (3, ""), (5, "m"), (4, "")]),
        ("ii - V - vi - IV", [(1, "m"), (4, ""), (5, "m"), (3, "")]),
        ("I - vi - ii - V", [(0, ""), (5, "m"), (1, "m"), (4, "")]),
        ("vi - ii - V - I", [(5, "m"), (1, "m"), (4, ""), (0, "")]),
        ("iii - vi - ii - V", [(2, "m"), (5, "m"), (1, "m"), (4, "")]),
        ("vi - IV - I - IV", [(5, "m"), (3, ""), (0, ""), (3, "")]),
    ],
    "Adoración": [
        ("I - IVmaj7 - V - vi", [(0, ""), (3, "maj7"), (4, ""), (5, "m")]),
        ("Imaj7 - IVmaj7 - V7 - Imaj7", [(0, "maj7"), (3, "maj7"), (4, "7"), (0, "maj7")]),
        ("vi - IV - Imaj7 - V", [(5, "m"), (3, ""), (0, "maj7"), (4, "")]),
        ("I - Vsus4 - V - vi", [(0, ""), (4, "sus4"), (4, ""), (5, "m")]),
        ("ii7 - V7 - Imaj7 - vi7", [(1, "m7"), (4, "7"), (0, "maj7"), (5, "m7")]),
        ("I - iii - IVmaj7 - Vsus4", [(0, ""), (2, "m"), (3, "maj7"), (4, "sus4")]),
        ("Imaj7 - vi7 - IVmaj7 - V7", [(0, "maj7"), (5, "m7"), (3, "maj7"), (4, "7")]),
        ("I - IVsus4 - IV - Vsus4", [(0, ""), (3, "sus4"), (3, ""), (4, "sus4")]),
    ],
}


def random_style_progression(rng: random.Random | None = None) -> tuple[str, str, list[tuple[int, str]]]:
    """Elige un estilo y una de sus progresiones al azar. Devuelve (estilo, nombre, grados/calidades)."""
    rng = rng or random
    style = rng.choice(list(STYLE_PROGRESSIONS))
    name, degree_qualities = rng.choice(STYLE_PROGRESSIONS[style])
    return style, name, degree_qualities


def _random_other_key(exclude_pc: int, rng: random.Random) -> int:
    choices = [pc for pc in range(12) if pc != exclude_pc]
    return rng.choice(choices)


def generate_question(rng: random.Random | None = None) -> dict:
    """Genera una pregunta: progresión en un tono origen, debe transportarse al tono destino.
    Ya no incluye opciones múltiples — el bot (handlers.py) arma el picker con
    todos los acordes posibles y el jugador construye la respuesta acorde por acorde."""
    rng = rng or random
    prog_idx = rng.randrange(len(COMMON_PROGRESSIONS))
    name, degrees = COMMON_PROGRESSIONS[prog_idx]
    origin_pc = rng.randrange(12)
    target_pc = _random_other_key(origin_pc, rng)

    origin_chords = build_progression(origin_pc, degrees)
    semitones = (target_pc - origin_pc) % 12
    correct_chords = transpose_progression(origin_chords, semitones)

    return {
        "progression_name": name,
        "prog_idx": prog_idx,
        "origin_pc": origin_pc,
        "target_pc": target_pc,
        "origin_key": NOTE_NAMES[origin_pc],
        "target_key": NOTE_NAMES[target_pc],
        "origin_chords": origin_chords,
        "correct_chords": correct_chords,
        "explanation": PROGRESSION_EXPLANATIONS.get(name),
    }
