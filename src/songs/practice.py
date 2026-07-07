"""Genera preguntas de transposición usando canciones reales del cancionero
(mismo formato que theory.progressions.generate_question, para reusar el
callback de respuesta ans|chosen|correct ya existente en el bot)."""

import random

from ..theory.notes import NOTE_NAMES, parse_chord, semitone_distance, transpose_progression

_MAX_CHORDS = 4


def _random_other_key(exclude_pc: int, rng: random.Random) -> int:
    choices = [pc for pc in range(12) if pc != exclude_pc]
    return rng.choice(choices)


def generate_song_question(song: dict, rng: random.Random | None = None) -> dict:
    rng = rng or random
    origin_pc, _, _ = parse_chord(song["tono"])
    target_pc = _random_other_key(origin_pc, rng)
    semitones = semitone_distance(origin_pc, target_pc)

    origin_chords = song["unique_chords"][:_MAX_CHORDS]
    correct_chords = transpose_progression(origin_chords, semitones)

    distractor_sets = []

    off_by_one = transpose_progression(origin_chords, (semitones + 1) % 12)
    if off_by_one != correct_chords:
        distractor_sets.append(off_by_one)

    off_by_minus_one = transpose_progression(origin_chords, (semitones - 1) % 12)
    if off_by_minus_one != correct_chords and off_by_minus_one not in distractor_sets:
        distractor_sets.append(off_by_minus_one)

    while len(distractor_sets) < 3:
        random_pc = _random_other_key(origin_pc, rng)
        candidate = transpose_progression(origin_chords, semitone_distance(origin_pc, random_pc))
        if candidate != correct_chords and candidate not in distractor_sets:
            distractor_sets.append(candidate)

    options = distractor_sets[:3] + [correct_chords]
    rng.shuffle(options)
    correct_index = options.index(correct_chords)

    return {
        "title": song["title"],
        "origin_key": song["tono"],
        "target_key": NOTE_NAMES[target_pc],
        "origin_chords": origin_chords,
        "correct_chords": correct_chords,
        "options": options,
        "correct_index": correct_index,
    }
