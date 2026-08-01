import json
import sqlite3
from datetime import datetime, timezone


CREATE_FEEDBACK_TABLE = """
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id TEXT NOT NULL,
    restaurant_name TEXT NOT NULL,
    liked INTEGER NOT NULL CHECK (liked IN (0, 1)),
    recommendation_tags TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def save_feedback(
    database_path,
    place_id,
    restaurant_name,
    liked,
    recommendation_tags,
):
    """Save one restaurant preference and return its database ID."""
    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(database_path) as connection:
        connection.execute(CREATE_FEEDBACK_TABLE)
        cursor = connection.execute(
            """
            INSERT INTO feedback (
                place_id,
                restaurant_name,
                liked,
                recommendation_tags,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                place_id,
                restaurant_name,
                int(liked),
                json.dumps(recommendation_tags),
                created_at,
            ),
        )

    return cursor.lastrowid


def list_feedback(database_path):
    """Return saved feedback in the order it was collected."""
    with sqlite3.connect(database_path) as connection:
        connection.execute(CREATE_FEEDBACK_TABLE)
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, place_id, restaurant_name, liked,
                   recommendation_tags, created_at
            FROM feedback
            ORDER BY id
            """
        ).fetchall()

    return [
        {
            **dict(row),
            "liked": bool(row["liked"]),
            "recommendation_tags": json.loads(row["recommendation_tags"]),
        }
        for row in rows
    ]
