"""Extrae título, tonalidades y acordes de los PDFs de cancionero (formato Jehová Sama)."""

import re
from pathlib import Path

from pypdf import PdfReader

CHORD_TOKEN_RE = re.compile(
    r"^[A-G](?:#|b)?"
    r"(?:m|maj7|maj9|sus4|sus2|sus|add9|add11|dim7|dim|aug|m7|m9|m6|7|9|6)?"
    r"(?:/[A-G](?:#|b)?)?$"
)

_SECTION_WORDS = (
    "Intro", "Verso", "PreCoro", "Pre-Coro", "Coro", "Puente",
    "Interludio", "Instrumental", "Solo", "Final", "Outro",
)
_SECTION_RE = re.compile(
    r"^(" + "|".join(_SECTION_WORDS) + r")\s*\d*\s*:?\s*(.*)$", re.IGNORECASE
)
_REPEAT_RE = re.compile(r"^[xX]\d+$")
_KEY_RE = re.compile(
    # Cada campo puede venir vacío (sin cambio de tono) o con varios tonos separados por
    # guiones (medleys, ej. "C - D"); solo se captura el primer tono de cada campo.
    r"Tono Original:\s*([A-G](?:#|b)?)?[^/\n]*/\s*Transportado:\s*([A-G](?:#|b)?)?"
)


def _clean_tokens(text: str) -> list[str]:
    text = text.replace("|", " ")
    tokens = []
    for tok in text.split():
        tok = tok.strip()
        if not tok or _REPEAT_RE.match(tok):
            continue
        tokens.append(tok)
    return tokens


def _is_chord_line(tokens: list[str]) -> bool:
    return bool(tokens) and all(CHORD_TOKEN_RE.match(t) for t in tokens)


def parse_song_pdf(path: Path) -> dict | None:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        return None  # PDF escaneado (imagen), sin texto extraíble

    key_match = _KEY_RE.search(text)
    tono_original = key_match.group(1) if key_match else None
    tono_transportado = key_match.group(2) if key_match else None
    # Tono efectivo del acorde tal como está escrito en la partitura: el transportado
    # si existe, si no el original (un campo vacío significa "sin cambio").
    tono = tono_transportado or tono_original

    chord_sequence: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        sec_match = _SECTION_RE.match(line)
        candidate = sec_match.group(2) if sec_match and sec_match.group(2) else line
        tokens = _clean_tokens(candidate)
        if _is_chord_line(tokens):
            chord_sequence.extend(tokens)

    seen = set()
    unique_chords = []
    for c in chord_sequence:
        if c not in seen:
            seen.add(c)
            unique_chords.append(c)

    return {
        "title": path.stem,
        "tono_original": tono_original,
        "tono_transportado": tono_transportado,
        "tono": tono,
        "chord_sequence": chord_sequence,
        "unique_chords": unique_chords,
    }


def parse_song_directory(directory: Path) -> list[dict]:
    songs = []
    for pdf_path in sorted(directory.glob("*.pdf")):
        song = parse_song_pdf(pdf_path)
        if song is not None:
            songs.append(song)
    return songs
