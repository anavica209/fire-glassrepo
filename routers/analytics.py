import hmac
import sqlite3
from contextlib import closing
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse

from app_constants import (
    FIELD_EMAIL,
    FIELD_ADMIN,
    FIELD_DURATIONS,
    FIELD_FORMATTED,
    FIELD_LABEL,
    FIELD_NAME,
    FIELD_ROWS,
    FIELD_SECONDS,
    FIELD_SECTION,
    FIELD_SECTION_TRACKING,
    FIELD_SESSION_ID,
    FIELD_USERNAME,
    FIELD_USER_KEY,
)
from core import (
    ANALYTICS_DB_PATH,
    SESSION_SECRET,
    SectionTrackingRequest,
    initialize_analytics_store,
    require_admin_session,
    require_session_user,
    templates,
)

router = APIRouter()


def _load_analytics_records():
    initialize_analytics_store()
    with closing(sqlite3.connect(ANALYTICS_DB_PATH, timeout=5)) as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(
            """
            SELECT
                user_key,
                MAX(username) AS username,
                ROUND(SUM(CASE WHEN section = 1 THEN duration_seconds ELSE 0 END), 1) AS section_1,
                ROUND(SUM(CASE WHEN section = 2 THEN duration_seconds ELSE 0 END), 1) AS section_2,
                ROUND(SUM(CASE WHEN section = 3 THEN duration_seconds ELSE 0 END), 1) AS section_3,
                ROUND(SUM(CASE WHEN section = 4 THEN duration_seconds ELSE 0 END), 1) AS section_4,
                ROUND(SUM(CASE WHEN section = 5 THEN duration_seconds ELSE 0 END), 1) AS section_5
            FROM section_time_events
            GROUP BY user_key
            ORDER BY username COLLATE NOCASE
            """
        ).fetchall()


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(
    request: Request,
    _admin: Annotated[dict[str, str], Depends(require_admin_session)],
):
    results = _load_analytics_records()
    rows = []
    for result in results:
        durations = [
            result[f"section_{section}"] or 0
            for section in range(1, 6)
        ]
        rows.append(
            {
                FIELD_USERNAME: result[FIELD_USERNAME],
                FIELD_DURATIONS: [
                    {
                        FIELD_SECTION: section,
                        FIELD_LABEL: label,
                        FIELD_SECONDS: seconds,
                        FIELD_FORMATTED: f"{int(seconds) // 60} min {int(seconds) % 60} s",
                    }
                    for section, label, seconds in zip(
                        range(1, 6),
                        (
                            "Bienvenida",
                            "Enfoque",
                            "El encuentro",
                            "Tu lectura",
                            "Integrar",
                        ),
                        durations,
                        strict=True,
                    )
                ],
            }
        )
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={FIELD_ROWS: rows, FIELD_ADMIN: _admin},
    )


@router.post("/api/analytics/section", status_code=status.HTTP_204_NO_CONTENT)
async def track_section(
    request: Request,
    tracking: SectionTrackingRequest,
    user: Annotated[dict[str, str], Depends(require_session_user)],
):
    setattr(request.state, FIELD_SECTION_TRACKING, {
        FIELD_USER_KEY: hmac.new(
            SESSION_SECRET.encode("utf-8"),
            user[FIELD_EMAIL].casefold().encode("utf-8"),
            "sha256",
        ).hexdigest(),
        FIELD_USERNAME: user[FIELD_NAME],
        FIELD_SESSION_ID: tracking.session_id,
        FIELD_SECTION: tracking.section,
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)

