"""Digitaciones estándar (posición abierta o cejilla) para las 12 tonalidades.

Cada forma es una lista de 6 valores, de la cuerda 6 (Mi grave) a la 1 (Mi agudo):
'x' = cuerda apagada, 0 = al aire, N = traste N.
Las tonalidades usan la misma ortografía que theory.notes.NOTE_NAMES (Db, Eb, F#, Ab, Bb).
"""

CHORD_SHAPES: dict[str, list] = {
    # Mayores
    "C": ["x", 3, 2, 0, 1, 0],
    "Db": ["x", 4, 6, 6, 6, 4],
    "D": ["x", "x", 0, 2, 3, 2],
    "Eb": ["x", "x", 1, 3, 4, 3],
    "E": [0, 2, 2, 1, 0, 0],
    "F": [1, 3, 3, 2, 1, 1],
    "F#": [2, 4, 4, 3, 2, 2],
    "G": [3, 2, 0, 0, 0, 3],
    "Ab": [4, 6, 6, 5, 4, 4],
    "A": ["x", 0, 2, 2, 2, 0],
    "Bb": ["x", 1, 3, 3, 3, 1],
    "B": ["x", 2, 4, 4, 4, 2],
    # Menores
    "Cm": ["x", 3, 5, 5, 4, 3],
    "Dbm": ["x", 4, 6, 6, 5, 4],
    "Dm": ["x", "x", 0, 2, 3, 1],
    "Ebm": ["x", "x", 1, 3, 4, 2],
    "Em": [0, 2, 2, 0, 0, 0],
    "Fm": [1, 3, 3, 1, 1, 1],
    "F#m": [2, 4, 4, 2, 2, 2],
    "Gm": [3, 5, 5, 3, 3, 3],
    "Abm": [4, 6, 6, 4, 4, 4],
    "Am": ["x", 0, 2, 2, 1, 0],
    "Bbm": ["x", 1, 3, 3, 2, 1],
    "Bm": ["x", 2, 4, 4, 3, 2],
    # Séptimas, maj7, m7 y sus4 — formas reales derivadas de los patrones movibles
    # CAGED (E-shape y A-shape) verificadas contra los acordes abiertos estándar
    # (E7, Em7, Emaj7, Esus4, A7, Am7, Amaj7, Asus4 coinciden exactamente con la
    # forma abierta conocida), o formas abiertas propias cuando son más comunes
    # que la cejilla equivalente (C, D, G).
    "C7": ["x", 3, 2, 3, 1, 0],
    "Cmaj7": ["x", 3, 2, 0, 0, 0],
    "Cm7": ["x", 3, 5, 3, 4, 3],
    "Csus4": ["x", 3, 3, 0, 1, 1],
    "Db7": ["x", 4, 6, 4, 6, 4],
    "Dbmaj7": ["x", 4, 6, 5, 6, 4],
    "Dbm7": ["x", 4, 6, 4, 5, 4],
    "Dbsus4": ["x", 4, 6, 6, 7, 4],
    "D7": ["x", "x", 0, 2, 1, 2],
    "Dmaj7": ["x", "x", 0, 2, 2, 2],
    "Dm7": ["x", "x", 0, 2, 1, 1],
    "Dsus4": ["x", "x", 0, 2, 3, 3],
    "Eb7": ["x", "x", 1, 3, 2, 3],
    "Ebmaj7": ["x", "x", 1, 3, 3, 3],
    "Ebm7": ["x", "x", 1, 3, 2, 2],
    "Ebsus4": ["x", "x", 1, 3, 4, 4],
    "E7": [0, 2, 0, 1, 0, 0],
    "Emaj7": [0, 2, 1, 1, 0, 0],
    "Em7": [0, 2, 0, 0, 0, 0],
    "Esus4": [0, 2, 2, 2, 0, 0],
    "F7": [1, 3, 1, 2, 1, 1],
    "Fmaj7": [1, 3, 2, 2, 1, 1],
    "Fm7": [1, 3, 1, 1, 1, 1],
    "Fsus4": [1, 3, 3, 3, 1, 1],
    "F#7": [2, 4, 2, 3, 2, 2],
    "F#maj7": [2, 4, 3, 3, 2, 2],
    "F#m7": [2, 4, 2, 2, 2, 2],
    "F#sus4": [2, 4, 4, 4, 2, 2],
    "G7": [3, 2, 0, 0, 0, 1],
    "Gmaj7": [3, 5, 4, 4, 3, 3],
    "Gm7": [3, 5, 3, 3, 3, 3],
    "Gsus4": [3, 5, 5, 5, 3, 3],
    "Ab7": [4, 6, 4, 5, 4, 4],
    "Abmaj7": [4, 6, 5, 5, 4, 4],
    "Abm7": [4, 6, 4, 4, 4, 4],
    "Absus4": [4, 6, 6, 6, 4, 4],
    "A7": ["x", 0, 2, 0, 2, 0],
    "Amaj7": ["x", 0, 2, 1, 2, 0],
    "Am7": ["x", 0, 2, 0, 1, 0],
    "Asus4": ["x", 0, 2, 2, 3, 0],
    "Bb7": ["x", 1, 3, 1, 3, 1],
    "Bbmaj7": ["x", 1, 3, 2, 3, 1],
    "Bbm7": ["x", 1, 3, 1, 2, 1],
    "Bbsus4": ["x", 1, 3, 3, 4, 1],
    "B7": ["x", 2, 4, 2, 4, 2],
    "Bmaj7": ["x", 2, 4, 3, 4, 2],
    "Bm7": ["x", 2, 4, 2, 3, 2],
    "Bsus4": ["x", 2, 4, 4, 5, 2],
}


# Acordes con bajo alterado (slash chords) que sí tienen una digitación real y sencilla
# (variante de un acorde abierto con una cuerda distinta al aire/apagada), en vez de solo
# tocar el acorde base ignorando el bajo. Claves en ortografía canónica (ver notes.NOTE_NAMES).
SLASH_CHORD_SHAPES: dict[str, list] = {
    "C/E": [0, 3, 2, 0, 1, 0],
    "C/G": [3, 3, 2, 0, 1, 0],
    "D/F#": [2, 0, 0, 2, 3, 2],
    "G/B": ["x", 2, 0, 0, 0, 3],
    "G/D": ["x", "x", 0, 0, 0, 3],
    "F/A": ["x", 0, 3, 2, 1, 1],
    "Bb/D": ["x", "x", 0, 3, 3, 1],
    "E/Ab": [4, 2, 2, 1, 0, 0],
}


def get_shape(chord_name: str) -> list:
    if chord_name not in CHORD_SHAPES:
        raise ValueError(f"No hay digitación conocida para: {chord_name!r}")
    return CHORD_SHAPES[chord_name]


def resolve_diagram(chord_name: str) -> tuple[list, str | None]:
    """Devuelve (forma, nota) para cualquier acorde, incluyendo acordes con calidad
    extendida (7, sus, maj7...) o con bajo alterado (slash). 'nota' es None si la forma
    es exacta, o un texto corto si es una aproximación (forma base simplificada y/o el
    bajo real no está representado en la digitación)."""
    from .notes import format_chord, NOTE_NAMES, parse_chord

    root_pc, quality, bass_pc = parse_chord(chord_name)
    canonical = format_chord(root_pc, quality, bass_pc)

    if canonical in CHORD_SHAPES:
        return CHORD_SHAPES[canonical], None
    if canonical in SLASH_CHORD_SHAPES:
        return SLASH_CHORD_SHAPES[canonical], None

    is_minor = quality.startswith("m") and not quality.startswith("maj")
    base_name = NOTE_NAMES[root_pc % 12] + ("m" if is_minor else "")
    if base_name not in CHORD_SHAPES:
        raise ValueError(f"No hay digitación conocida para: {chord_name!r}")

    notes = []
    base_quality = "m" if is_minor else ""
    if quality != base_quality:
        notes.append("forma simplificada")
    if bass_pc is not None and bass_pc % 12 != root_pc % 12:
        notes.append(f"bajo real: {NOTE_NAMES[bass_pc % 12]}")
    note = " · ".join(notes) if notes else None
    return CHORD_SHAPES[base_name], note
