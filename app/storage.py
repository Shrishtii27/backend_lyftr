from datetime import datetime
from typing import Optional, List, Tuple

from app.models import get_connection


def save_message(payload: dict) -> bool:
    """
    Insert a message into the database.
    Returns True if inserted, False if duplicate.
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO messages (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload["message_id"],
                payload["from"],
                payload["to"],
                payload["ts"],
                payload.get("text"),
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        connection.commit()
        created = True
    except Exception:
        # Primary key violation → duplicate message
        created = False
    finally:
        connection.close()

    return created


def list_messages(
    limit: int,
    offset: int,
    from_msisdn: Optional[str],
    since: Optional[str],
    q: Optional[str],
) -> Tuple[List[dict], int]:
    connection = get_connection()
    cursor = connection.cursor()

    filters = []
    values = []

    if from_msisdn:
        filters.append("from_msisdn = ?")
        values.append(from_msisdn)

    if since:
        filters.append("ts >= ?")
        values.append(since)

    if q:
        filters.append("LOWER(text) LIKE ?")
        values.append(f"%{q.lower()}%")

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    total_sql = f"SELECT COUNT(*) FROM messages {where_clause}"
    total_rows = cursor.execute(total_sql, values).fetchone()[0]

    data_sql = f"""
        SELECT
            message_id,
            from_msisdn,
            to_msisdn,
            ts,
            text
        FROM messages
        {where_clause}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
    """

    rows = cursor.execute(
        data_sql,
        values + [limit, offset],
    ).fetchall()

    connection.close()

    messages = [
        {
            "message_id": row["message_id"],
            "from": row["from_msisdn"],
            "to": row["to_msisdn"],
            "ts": row["ts"],
            "text": row["text"],
        }
        for row in rows
    ]

    return messages, total_rows


def get_stats():
    connection = get_connection()
    cursor = connection.cursor()

    total_messages = cursor.execute(
        "SELECT COUNT(*) FROM messages"
    ).fetchone()[0]

    distinct_senders = cursor.execute(
        "SELECT COUNT(DISTINCT from_msisdn) FROM messages"
    ).fetchone()[0]

    top_senders = cursor.execute(
        """
        SELECT from_msisdn, COUNT(*) AS count
        FROM messages
        GROUP BY from_msisdn
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()

    sender_stats = [
        {"from": row["from_msisdn"], "count": row["count"]}
        for row in top_senders
    ]

    first_ts = cursor.execute(
        "SELECT MIN(ts) FROM messages"
    ).fetchone()[0]

    last_ts = cursor.execute(
        "SELECT MAX(ts) FROM messages"
    ).fetchone()[0]

    connection.close()

    return {
        "total_messages": total_messages,
        "senders_count": distinct_senders,
        "messages_per_sender": sender_stats,
        "first_message_ts": first_ts,
        "last_message_ts": last_ts,
    }



