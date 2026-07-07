"""Progresiones diatónicas comunes y generación de preguntas de transposición."""

import random

from .notes import NOTE_NAMES, format_chord, transpose_progression

MAJOR_SCALE_STEPS = [0, 2, 4, 5, 7, 9, 11]
# Calidad del acorde diatónico para cada grado (I..vii). '' = mayor.
DEGREE_QUALITY = ["", "m", "m", "", "", "m", "dim"]

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


def _random_other_key(exclude_pc: int, rng: random.Random) -> int:
    choices = [pc for pc in range(12) if pc != exclude_pc]
    return rng.choice(choices)


def generate_question(rng: random.Random | None = None) -> dict:
    """Genera una pregunta: progresión en un tono origen, debe transportarse al tono destino."""
    rng = rng or random
    name, degrees = rng.choice(COMMON_PROGRESSIONS)
    origin_pc = rng.randrange(12)
    target_pc = _random_other_key(origin_pc, rng)

    origin_chords = build_progression(origin_pc, degrees)
    semitones = (target_pc - origin_pc) % 12
    correct_chords = transpose_progression(origin_chords, semitones)

    distractor_sets = []

    # Distractor 1: desplazamiento correcto pero un semitono de más.
    off_by_one = transpose_progression(origin_chords, (semitones + 1) % 12)
    if off_by_one != correct_chords:
        distractor_sets.append(off_by_one)

    # Distractor 2: desplazamiento correcto pero un semitono de menos.
    off_by_minus_one = transpose_progression(origin_chords, (semitones - 1) % 12)
    if off_by_minus_one != correct_chords and off_by_minus_one not in distractor_sets:
        distractor_sets.append(off_by_minus_one)

    # Distractor 3: mismo patrón, tonalidad totalmente distinta (aleatoria).
    while len(distractor_sets) < 3:
        random_pc = _random_other_key(origin_pc, rng)
        candidate = build_progression(random_pc, degrees)
        if candidate != correct_chords and candidate not in distractor_sets:
            distractor_sets.append(candidate)

    options = distractor_sets[:3] + [correct_chords]
    rng.shuffle(options)
    correct_index = options.index(correct_chords)

    return {
        "progression_name": name,
        "origin_key": NOTE_NAMES[origin_pc],
        "target_key": NOTE_NAMES[target_pc],
        "origin_chords": origin_chords,
        "correct_chords": correct_chords,
        "options": options,
        "correct_index": correct_index,
        "explanation": PROGRESSION_EXPLANATIONS.get(name),
    }
