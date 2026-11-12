import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import APP_DIR, COOKIE_SECURE, SESSION_SECRET
from app.core.constants import (
    FIELD_SECTION,
    FIELD_SECTION_TRACKING,
    FIELD_SESSION_ID,
    FIELD_STARTED_AT,
    FIELD_USER_KEY,
    FIELD_USERNAME,
)
from app.domain.core import (
    active_section_sessions,
    save_section_duration,
)
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.pages import router as pages_router
from app.api.readings import router as readings_router

app = FastAPI(title="Fire glass")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=COOKIE_SECURE,
)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")


@app.middleware("http")
async def record_section_time(request: Request, call_next):
    response = await call_next(request)
    event = getattr(request.state, FIELD_SECTION_TRACKING, None)
    if event is None or response.status_code >= 400:
        return response

    tracking_key = (event[FIELD_USER_KEY], str(event[FIELD_SESSION_ID]))
    current = active_section_sessions.get(tracking_key)
    next_section = event[FIELD_SECTION]
    if current is not None and current[FIELD_SECTION] != next_section:
        elapsed = max(0.0, time.monotonic() - current[FIELD_STARTED_AT])
        if elapsed > 0:
            save_section_duration(
                current[FIELD_USER_KEY],
                current[FIELD_USERNAME],
                current[FIELD_SECTION],
                elapsed,
            )
        del active_section_sessions[tracking_key]

    if next_section is not None and tracking_key not in active_section_sessions:
        active_section_sessions[tracking_key] = {
            FIELD_USER_KEY: event[FIELD_USER_KEY],
            FIELD_USERNAME: event[FIELD_USERNAME],
            FIELD_SECTION: next_section,
            FIELD_STARTED_AT: time.monotonic(),
        }
    return response


app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(readings_router)


    # required for docker config when using postgres 
    # def get_db_password():
    # secret_path = os.getenv("DB_PASSWORD_FILE")
    # if secret_path and os.path.exists(secret_path):
    #     with open(secret_path, "r") as f:
    #         return f.read().strip()
    # return os.getenv("DB_PASSWORD", "") 

@app.get("/health")
def health():
    return {"status": "ok", "env": os.getenv("APP_ENV")}