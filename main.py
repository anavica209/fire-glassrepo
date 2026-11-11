import os
import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from core import (
    BASE_DIR,
    SESSION_SECRET,
    active_section_sessions,
    save_section_duration,
)
from routers.analytics import router as analytics_router
from routers.auth import router as auth_router
from routers.pages import router as pages_router
from routers.readings import router as readings_router

app = FastAPI(title="Fire glass")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=os.getenv("COOKIE_SECURE", "false").lower() == "true",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.middleware("http")
async def record_section_time(request: Request, call_next):
    response = await call_next(request)
    event = getattr(request.state, "section_tracking", None)
    if event is None or response.status_code >= 400:
        return response

    tracking_key = (event["user_key"], str(event["session_id"]))
    current = active_section_sessions.get(tracking_key)
    next_section = event["section"]
    if current is not None and current["section"] != next_section:
        elapsed = max(0.0, time.monotonic() - current["started_at"])
        if elapsed > 0:
            save_section_duration(
                current["user_key"],
                current["username"],
                current["section"],
                elapsed,
            )
        del active_section_sessions[tracking_key]

    if next_section is not None and tracking_key not in active_section_sessions:
        active_section_sessions[tracking_key] = {
            "user_key": event["user_key"],
            "username": event["username"],
            "section": next_section,
            "started_at": time.monotonic(),
        }
    return response


app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(readings_router)
