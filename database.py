import sqlite3
import threading


_local = threading.local()


def get_connection(db_path: str) -> sqlite3.Connection:
    """Return a per-thread SQLite connection."""
    if not hasattr(_local, "conn") or _local.db_path != db_path:
        _local.conn = sqlite3.connect(db_path)
        _local.db_path = db_path
        _init_db(_local.conn)
    return _local.conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            text     TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def save_note(db_path: str, user_id: int, text: str) -> None:
    conn = get_connection(db_path)
    conn.execute("INSERT INTO notes (user_id, text) VALUES (?, ?)", (user_id, text))
    conn.commit()


def get_last_note(db_path: str, user_id: int) -> str | None:
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT text FROM notes WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    return row[0] if row else None


def search_notes(db_path: str, user_id: int, keyword: str) -> list[str]:
    conn = get_connection(db_path)
    escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = conn.execute(
        "SELECT text FROM notes WHERE user_id = ? AND text LIKE ? ESCAPE '\\' ORDER BY id DESC",
        (user_id, f"%{escaped}%"),
    ).fetchall()
    return [r[0] for r in rows]
