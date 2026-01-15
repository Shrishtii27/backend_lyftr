import sqlite3
from app.config import DATABASE_URL


def _extract_sqlite_path(db_url: str) -> str:
    """
    Convert sqlite DATABASE_URL into a filesystem path.
    Example: sqlite:////data/app.db -> /data/app.db
    """
    return db_url.replace("sqlite:///", "")


def get_connection():
    db_path = _extract_sqlite_path(DATABASE_URL)

    connection = sqlite3.connect(
        db_path,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            from_msisdn TEXT NOT NULL,
            to_msisdn TEXT NOT NULL,
            ts TEXT NOT NULL,
            text TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()



