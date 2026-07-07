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


def transpose_chord(chord: str, semitones: int) -> str:
    pc, quality, bass_pc = parse_chord(chord)
    new_bass = None if bass_pc is None else bass_pc + semitones
    return format_chord(pc + semitones, quality, new_bass)


def transpose_progression(chords: list[str], semitones: int) -> list[str]:
    return [transpose_chord(c, semitones) for c in chords]


def semitone_distance(from_pc: int, to_pc: int) -> int:
    """Semitonos (0-11) para ir de una tonalidad a otra, siempre hacia arriba."""
    return (to_pc - from_pc) % 12
