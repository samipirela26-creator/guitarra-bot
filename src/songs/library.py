"""Carga el catálogo de canciones ya parseado (ver parser.py -> data/songs.json)."""

import json
from functools import lru_cache

from ..config import BASE_DIR

SONGS_PATH = BASE_DIR / "data" / "songs.json"


@lru_cache(maxsize=1)
def load_songs() -> list[dict]:
    with open(SONGS_PATH, encoding="utf-8") as f:
        return json.load(f)
