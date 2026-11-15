import sqlite3
from datetime import datetime, timezone

from scripts.import_sqlite_analytics import read_legacy_events


def test_read_legacy_events_preserves_timestamps_and_primary_keys(tmp_path):
    database_path = tmp_path / "legacy.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE section_time_events (
                id INTEGER PRIMARY KEY,
                user_key TEXT NOT NULL,
                username TEXT NOT NULL,
                section INTEGER NOT NULL,
                duration_seconds REAL NOT NULL,
                recorded_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT INTO section_time_events VALUES (?, ?, ?, ?, ?, ?)",
            (17, "hashed-key", "Demo", 2, 12.5, "2024-01-02T03:04:05+00:00"),
        )

    events = read_legacy_events(database_path)

    assert events == [
        {
            "id": 17,
            "user_key": "hashed-key",
            "username": "Demo",
            "section": 2,
            "duration_seconds": 12.5,
            "recorded_at": datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        }
    ]
