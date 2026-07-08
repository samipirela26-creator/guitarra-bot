"""Genera preguntas de transposición usando canciones reales del cancionero.
Ya no arma opciones múltiples: el bot (handlers.py) construye un picker con
todos los acordes posibles y el jugador arma la respuesta acorde por acorde
(ver theory.chord_shapes.simplify_chord_name para cómo se normaliza la
respuesta correcta cuando la canción trae un acorde con calidad no soportada
o bajo alterado)."""

import random

from ..theory.notes import NOTE_NAMES, parse_chord, semitone_distance, transpose_progression

# Tope de acordes reales que se muestran/usan en /canciones. NO puede ser
# "el largo real de la canción" sin límite: el picker "arma la respuesta"
# codifica la selección acumulada en el callback_data del botón
# (formato "cbld|{song_idx}|{target_pc}|{sel_csv}|{chord}", ver
# bot/handlers.py), y Telegram limita callback_data a 64 bytes.
# Peor caso medido (índice de canción y tono destino de 2 dígitos, acorde
# más largo de ALL_EXTENDED_CHORDS = 6 chars, ej. "Abmaj7", repetido en cada
# selección): con 7 acordes el botón más pesado pesa 59 bytes; con 8 acordes
# ya pesa 66 bytes y Telegram rechazaría el callback. Por eso 7 es el tope
# seguro más alto posible (cualquier canción con más acordes únicos, ej.
# "Gracias, Dios" con 15, se trunca a los primeros 7 — no ideal, pero mejor
# que el límite anterior de 4, que ni siquiera cubría canciones simples de 5
# acordes como "Un Millón").
MAX_CHORDS = 7


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
