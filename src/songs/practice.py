"""Genera preguntas de transposición usando canciones reales del cancionero.
Ya no arma opciones múltiples: el bot (handlers.py) construye un picker con
todos los acordes posibles y el jugador arma la respuesta acorde por acorde
(ver theory.chord_shapes.simplify_chord_name para cómo se normaliza la
respuesta correcta cuando la canción trae un acorde con calidad no soportada
o bajo alterado)."""

import random

from ..theory.notes import NOTE_NAMES, parse_chord, semitone_distance, transpose_progression

MAX_CHORDS = 4


def _random_other_key(exclude_pc: int, rng: random.Random) -> int:
    choices = [pc for pc in range(12) if pc != exclude_pc]
    return rng.choice(choices)


def song_origin_chords(song: dict) -> list[str]:
    return song["unique_chords"][:MAX_CHORDS]


def generate_song_question(song: dict, rng: random.Random | None = None) -> dict:
    rng = rng or random
    origin_pc, _, _ = parse_chord(song["tono"])
    target_pc = _random_other_key(origin_pc, rng)
    semitones = semitone_distance(origin_pc, target_pc)

    origin_chords = song_origin_chords(song)
    correct_chords = transpose_progression(origin_chords, semitones)

    return {
        "title": song["title"],
        "origin_pc": origin_pc,
        "target_pc": target_pc,
        "origin_key": song["tono"],
        "target_key": NOTE_NAMES[target_pc],
        "origin_chords": origin_chords,
        "correct_chords": correct_chords,
    }
