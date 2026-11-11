import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from typing import Annotated, TypedDict
from uuid import UUID

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, model_validator

from app.core.config import (
    ANALYTICS_DB_PATH,
    APP_DIR,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    JWT_SECRET,
    SESSION_SECRET,
)
from app.core.constants import (
    ADMIN_ROLE,
    DEMO_EMAIL,
    FIELD_CATEGORY,
    FIELD_CARDS,
    FIELD_EMAIL,
    FIELD_NAME,
    FIELD_QUESTION,
    FIELD_ROLE,
    FIELD_SECTION,
    FIELD_SESSION_ID,
    FIELD_SUBJECT,
    FIELD_USER,
    POSITIONS,
)
from app.domain.cards import ReadingCard
from app.domain.categories import CategoryKey

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

templates = Jinja2Templates(directory=APP_DIR / "templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

oauth = OAuth()
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

class ReadingRequest(BaseModel):
    category: CategoryKey = Field(alias=FIELD_CATEGORY)
    question: str = Field(default="", max_length=500, alias=FIELD_QUESTION)


class DownloadReadingRequest(BaseModel):
    category: CategoryKey = Field(alias=FIELD_CATEGORY)
    cards: list[ReadingCard] = Field(
        min_length=3, max_length=3, alias=FIELD_CARDS
    )

    @model_validator(mode="after")
    def validate_cards(self):
        if tuple(card.position for card in self.cards) != POSITIONS:
            raise ValueError("La lectura debe incluir las tres posiciones en orden.")
        if len({card.name for card in self.cards}) != len(self.cards):
            raise ValueError("La lectura no puede repetir cartas.")
        return self


class SectionTrackingRequest(BaseModel):
    session_id: UUID = Field(alias=FIELD_SESSION_ID)
    section: int | None = Field(default=None, ge=1, le=5, alias=FIELD_SECTION)


class ActiveSectionSession(TypedDict):
    user_key: str
    username: str
    section: int
    started_at: float


active_section_sessions: dict[tuple[str, str], ActiveSectionSession] = {}


def initialize_analytics_store() -> None:
    with closing(sqlite3.connect(ANALYTICS_DB_PATH, timeout=5)) as connection:
        with connection:
            table = connection.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type = 'table' AND name = 'section_time_events'"
            ).fetchone()
            if table is None:
                _create_section_time_events_table(connection, "section_time_events")
            elif "BETWEEN1AND4" in "".join(table[0].upper().split()):
                _create_section_time_events_table(
                    connection, "section_time_events_v5"
                )
                connection.execute(
                    """
                    INSERT INTO section_time_events_v5
                        (id, user_key, username, section, duration_seconds, recorded_at)
                    SELECT id, user_key, username, section, duration_seconds, recorded_at
                    FROM section_time_events
                    """
                )
                connection.execute("DROP TABLE section_time_events")
                connection.execute(
                    "ALTER TABLE section_time_events_v5 "
                    "RENAME TO section_time_events"
                )


def _create_section_time_events_table(
    connection: sqlite3.Connection, table_name: str
) -> None:
    connection.execute(
        f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY,
            user_key TEXT NOT NULL,
            username TEXT NOT NULL,
            section INTEGER NOT NULL CHECK (section BETWEEN 1 AND 5),
            duration_seconds REAL NOT NULL,
            recorded_at TEXT NOT NULL
        )
        """
    )


def save_section_duration(
    user_key: str,
    username: str,
    section: int,
    duration_seconds: float,
) -> None:
    initialize_analytics_store()
    with closing(sqlite3.connect(ANALYTICS_DB_PATH, timeout=5)) as connection:
        with connection:
            connection.execute(
                """
                INSERT INTO section_time_events
                    (user_key, username, section, duration_seconds, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_key,
                    username,
                    section,
                    duration_seconds,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )


def signed_in_user(request: Request) -> dict[str, str] | None:
    user = request.session.get(FIELD_USER)
    return user if isinstance(user, dict) else None


def require_session_user(request: Request) -> dict[str, str]:
    user = signed_in_user(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inicia sesión para continuar.",
        )
    return user


def require_admin_session(request: Request) -> dict[str, str]:
    user = require_session_user(request)
    if user.get(FIELD_ROLE) != ADMIN_ROLE or user.get(FIELD_EMAIL) != DEMO_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analytics está disponible solo para el usuario administrador.",
        )
    return user




def create_access_token(user: dict[str, str]) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            FIELD_SUBJECT: user[FIELD_EMAIL],
            FIELD_EMAIL: user[FIELD_EMAIL],
            FIELD_NAME: user[FIELD_NAME],
            "iat": now,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


async def require_user(
    token: Annotated[str, Security(oauth2_scheme)],
) -> dict[str, str]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="El token de acceso es inválido o expiró.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get(FIELD_EMAIL)
        name = payload.get(FIELD_NAME)
        subject = payload.get(FIELD_SUBJECT)
        if (
            not all(isinstance(value, str) and value for value in (email, name, subject))
            or subject != email
        ):
            raise unauthorized
        return {FIELD_EMAIL: email, FIELD_NAME: name}
    except jwt.InvalidTokenError as exc:
        raise unauthorized from exc
