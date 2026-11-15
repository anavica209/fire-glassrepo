import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy import Numeric, case, cast, func, select

from app.core.config import SESSION_SECRET
from app.core.constants import (
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
from app.core.database import engine, section_time_events
from app.domain.core import (
    SectionTrackingRequest,
    require_admin_session,
    require_session_user,
    templates,
)

router = APIRouter()


async def _load_analytics_records():
    "Tracked times for the users in the different sections of the readings"
    section_totals = [
        func.round(
            cast(
                func.sum(
                    case(
                        (
                            section_time_events.c.section == section,
                            section_time_events.c.duration_seconds,
                        ),
                        else_=0.0,
                    )
                ),
                Numeric,
            ),
            1,
        ).label(f"section_{section}")
        for section in range(1, 6)
    ]
    statement = (
        select(
            section_time_events.c.user_key,
            func.max(section_time_events.c.username).label(FIELD_USERNAME),
            *section_totals,
        )
        .group_by(section_time_events.c.user_key)
        .order_by(func.lower(func.max(section_time_events.c.username)))
    )
    async with engine.connect() as connection:
        result = await connection.execute(statement)
        return result.mappings().all()


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(
    request: Request,
    _admin: Annotated[dict[str, str], Depends(require_admin_session)],
):
    "Display the tracked times for the users in the table in the different sections of the readings"
    results = await _load_analytics_records()
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
    "Track how much time a user spent in a section"
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
