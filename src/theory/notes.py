"""Utilidades básicas de teoría musical: notas, escalas y transposición."""

import re

# Ortografía preferida por clase de altura (pitch class 0-11), la más común entre guitarristas.
NOTE_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

_NOTE_TO_PC = {}
for pc, name in enumerate(NOTE_NAMES):
    _NOTE_TO_PC[name] = pc
# Alias enarmónicos que el usuario podría escribir.
_ALIASES = {
    "C#": "Db", "D#": "Eb", "Gb": "F#", "G#": "Ab", "A#": "Bb",
    "Cb": "B", "Fb": "E", "E#": "F", "B#": "C",
}
for alias, canonical in _ALIASES.items():
    _NOTE_TO_PC[alias] = _NOTE_TO_PC[canonical]

# Raíz + calidad (todo lo que no sea la nota) + bajo opcional tras "/" (acordes con inversión, ej. D/F#).
CHORD_RE = re.compile(r"^([A-G](?:#|b)?)([^/]*)(?:/([A-G](?:#|b)?))?$")


def parse_chord(chord: str) -> tuple[int, str, int | None]:
    """'D/F#' -> (2, '', 6). 'F#m7' -> (6, 'm7', None). ValueError si la raíz no es válida."""
    match = CHORD_RE.match(chord.strip())
    if not match:
        raise ValueError(f"No se pudo interpretar el acorde: {chord!r}")
    root, quality, bass = match.groups()
    if root not in _NOTE_TO_PC:
        raise ValueError(f"Nota raíz desconocida: {root!r}")
    if bass is not None and bass not in _NOTE_TO_PC:
        raise ValueError(f"Nota de bajo desconocida: {bass!r}")
    bass_pc = _NOTE_TO_PC[bass] if bass else None
    return _NOTE_TO_PC[root], quality, bass_pc


def format_chord(pitch_class: int, quality: str, bass_pitch_class: int | None = None) -> str:
    text = f"{NOTE_NAMES[pitch_class % 12]}{quality}"
    if bass_pitch_class is not None:
        text += f"/{NOTE_NAMES[bass_pitch_class % 12]}"
    return text


# --- Deletreo enarmónico según la tonalidad -----------------------------------
# NOTE_NAMES fija una sola ortografía por clase de altura (Db, Eb, F#, Ab, Bb),
# lo cual es cómodo pero enarmónicamente incorrecto dentro de una tonalidad: en
# Si mayor el ii grado debe ser C#m, no Dbm. Estas utilidades deletrean cada
# grado de una escala usando cada letra (A-G) UNA sola vez a partir de la tónica,
# que es la regla correcta de la notación diatónica.
_LETTER_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_LETTERS = ["C", "D", "E", "F", "G", "A", "B"]


def _spell_pc(pitch_class: int, letter: str) -> str:
    """Deletrea una clase de altura forzando cierta letra (A-G), añadiendo los
    sostenidos/bemoles que hagan falta. Ej: _spell_pc(1, 'C') -> 'C#',
    _spell_pc(1, 'D') -> 'Db', _spell_pc(5, 'E') -> 'E#'."""
    diff = (pitch_class - _LETTER_PC[letter]) % 12
    if diff > 6:
        diff -= 12  # queda en el rango -5..6 (bemoles negativos, sostenidos positivos)
    if diff == 0:
        return letter
    return letter + ("#" * diff if diff > 0 else "b" * -diff)


def diatonic_spelling(tonic_name: str, scale_steps: list[int]) -> dict[int, str]:
    """Mapa {clase de altura: nombre correctamente deletreado} para cada grado de
    la escala que arranca en `tonic_name` (ej. 'F#', 'Eb'). Usa cada letra A-G una
    sola vez. Las notas fuera de la escala NO están en el mapa; el llamador debe
    caer de vuelta a NOTE_NAMES para ellas."""
    if tonic_name not in _NOTE_TO_PC:
        raise ValueError(f"Tónica desconocida: {tonic_name!r}")
    start = _LETTERS.index(tonic_name[0])
    tonic_pc = _NOTE_TO_PC[tonic_name]
    mapping: dict[int, str] = {}
    for i, step in enumerate(scale_steps):
        pc = (tonic_pc + step) % 12
        mapping[pc] = _spell_pc(pc, _LETTERS[(start + i) % 7])
    return mapping


def format_chord_in_key(
    pitch_class: int,
    quality: str,
    spelling: dict[int, str],
    bass_pitch_class: int | None = None,
) -> str:
    """Como format_chord, pero usa el deletreo de `spelling` (ver diatonic_spelling)
    para las notas dentro de la tonalidad, cayendo a NOTE_NAMES para el resto."""
    root = spelling.get(pitch_class % 12, NOTE_NAMES[pitch_class % 12])
    text = f"{root}{quality}"
    if bass_pitch_class is not None:
        bass = spelling.get(bass_pitch_class % 12, NOTE_NAMES[bass_pitch_class % 12])
        text += f"/{bass}"
    return text


def transpose_chord(chord: str, semitones: int) -> str:
    pc, quality, bass_pc = parse_chord(chord)
    new_bass = None if bass_pc is None else bass_pc + semitones
    return format_chord(pc + semitones, quality, new_bass)


def transpose_progression(chords: list[str], semitones: int) -> list[str]:
    return [transpose_chord(c, semitones) for c in chords]


def semitone_distance(from_pc: int, to_pc: int) -> int:
    """Semitonos (0-11) para ir de una tonalidad a otra, siempre hacia arriba."""
    return (to_pc - from_pc) % 12
