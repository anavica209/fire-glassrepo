import hmac
import sqlite3
from contextlib import closing
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse

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


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(
    request: Request,
    _admin: Annotated[dict[str, str], Depends(require_admin_session)],
):
    initialize_analytics_store()
    with closing(sqlite3.connect(ANALYTICS_DB_PATH, timeout=5)) as connection:
        connection.row_factory = sqlite3.Row
        results = connection.execute(
            """
            SELECT
                user_key,
                MAX(username) AS username,
                ROUND(SUM(CASE WHEN section = 1 THEN duration_seconds ELSE 0 END), 1) AS section_1,
                ROUND(SUM(CASE WHEN section = 2 THEN duration_seconds ELSE 0 END), 1) AS section_2,
                ROUND(SUM(CASE WHEN section = 3 THEN duration_seconds ELSE 0 END), 1) AS section_3,
                ROUND(SUM(CASE WHEN section = 4 THEN duration_seconds ELSE 0 END), 1) AS section_4
            FROM section_time_events
            GROUP BY user_key
            ORDER BY username COLLATE NOCASE
            """
        ).fetchall()

    rows = []
    for result in results:
        durations = [
            result[f"section_{section}"] or 0
            for section in range(1, 5)
        ]
        rows.append(
            {
                "username": result["username"],
                "durations": [
                    {
                        "section": section,
                        "label": label,
                        "seconds": seconds,
                        "formatted": f"{int(seconds) // 60} min {int(seconds) % 60} s",
                    }
                    for section, label, seconds in zip(
                        range(1, 5),
                        ("Bienvenida", "Enfoque", "Tirada", "Interpretación"),
                        durations,
                        strict=True,
                    )
                ],
            }
        )
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={"rows": rows, "admin": _admin},
    )


@router.post("/api/analytics/section", status_code=status.HTTP_204_NO_CONTENT)
async def track_section(
    request: Request,
    tracking: SectionTrackingRequest,
    user: Annotated[dict[str, str], Depends(require_session_user)],
):
    request.state.section_tracking = {
        "user_key": hmac.new(
            SESSION_SECRET.encode("utf-8"),
            user["email"].casefold().encode("utf-8"),
            "sha256",
        ).hexdigest(),
        "username": user["name"],
        "session_id": tracking.session_id,
        "section": tracking.section,
    }
    return Response(status_code=status.HTTP_204_NO_CONTENT)
