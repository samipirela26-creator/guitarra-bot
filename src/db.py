import sqlite3

from .config import DB_PATH

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS game_stats (
    user_id INTEGER PRIMARY KEY,
    correct INTEGER NOT NULL DEFAULT 0,
    incorrect INTEGER NOT NULL DEFAULT 0,
    streak INTEGER NOT NULL DEFAULT 0,
    best_streak INTEGER NOT NULL DEFAULT 0
)
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(_CREATE_TABLE)
    return conn


def _row_to_stats(row: tuple) -> dict:
    return {"correct": row[0], "incorrect": row[1], "streak": row[2], "best_streak": row[3]}


def get_stats(user_id: int) -> dict:
    conn = _connect()
    with conn:
        conn.execute("INSERT OR IGNORE INTO game_stats (user_id) VALUES (?)", (user_id,))
        row = conn.execute(
            "SELECT correct, incorrect, streak, best_streak FROM game_stats WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    conn.close()
    return _row_to_stats(row)


def record_result(user_id: int, correct: bool) -> dict:
    conn = _connect()
    with conn:
        conn.execute("INSERT OR IGNORE INTO game_stats (user_id) VALUES (?)", (user_id,))
        if correct:
            conn.execute(
                """UPDATE game_stats
                   SET correct = correct + 1,
                       streak = streak + 1,
                       best_streak = MAX(best_streak, streak + 1)
                   WHERE user_id = ?""",
                (user_id,),
            )
        else:
            conn.execute(
                "UPDATE game_stats SET incorrect = incorrect + 1, streak = 0 WHERE user_id = ?",
                (user_id,),
            )
        row = conn.execute(
            "SELECT correct, incorrect, streak, best_streak FROM game_stats WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    conn.close()
    return _row_to_stats(row)
