"""Círculo de quintas: orden de tonalidades y sus relativas menores."""

from .notes import NOTE_NAMES, parse_chord

# Orden en el sentido horario del círculo de quintas, empezando en Do.
CIRCLE_MAJOR_ORDER = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"]

# Relativa menor de cada tonalidad mayor (mismo índice que CIRCLE_MAJOR_ORDER).
RELATIVE_MINOR = ["Am", "Em", "Bm", "F#m", "C#m", "G#m", "Ebm", "Bbm", "Fm", "Cm", "Gm", "Dm"]


def circle_position(pitch_class: int) -> int:
    """Posición (0-11) de una clase de altura dentro del círculo de quintas."""
    name = NOTE_NAMES[pitch_class % 12]
    return CIRCLE_MAJOR_ORDER.index(name)


def neighbors(pitch_class: int) -> tuple[int, int]:
    """Devuelve (dominante, subdominante): vecinos en el círculo de quintas."""
    pos = circle_position(pitch_class)
    dominant = parse_chord(CIRCLE_MAJOR_ORDER[(pos + 1) % 12])[0]
    subdominant = parse_chord(CIRCLE_MAJOR_ORDER[(pos - 1) % 12])[0]
    return dominant, subdominant
