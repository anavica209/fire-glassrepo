"""Import existing SQLite analytics into the PostgreSQL database."""

import asyncio
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.core.config import DATA_DIR
from app.core.database import engine, section_time_events

LEGACY_DATABASE = DATA_DIR / "fire_glass_analytics.db"


def read_legacy_events(path: Path = LEGACY_DATABASE) -> list[dict[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró la base SQLite: {path}")

    with sqlite3.connect(path) as connection:
        rows = connection.execute(
            """
            SELECT id, user_key, username, section, duration_seconds, recorded_at
            FROM section_time_events
            ORDER BY id
            """
        ).fetchall()

    events = []
    for row in rows:
        recorded_at = datetime.fromisoformat(row[5])
        if recorded_at.tzinfo is None:
            recorded_at = recorded_at.replace(tzinfo=timezone.utc)
        events.append(
            {
                "id": row[0],
                "user_key": row[1],
                "username": row[2],
                "section": row[3],
                "duration_seconds": row[4],
                "recorded_at": recorded_at,
            }
        )
    return events


async def import_events() -> int:
    events = read_legacy_events()
    async with engine.begin() as connection:
        if events:
            statement = insert(section_time_events).values(events)
            await connection.execute(
                statement.on_conflict_do_nothing(
                    index_elements=[section_time_events.c.id]
                )
            )
        await connection.execute(
            text(
                "SELECT setval("
                "pg_get_serial_sequence('section_time_events', 'id'), "
                "COALESCE(MAX(id), 1), MAX(id) IS NOT NULL"
                ") FROM section_time_events"
            )
        )
    return len(events)


async def main() -> None:
    try:
        imported_count = await import_events()
        print(f"SQLite analytics import completed ({imported_count} source rows).")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
