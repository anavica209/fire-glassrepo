"Base configurations like env variables."
import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL, make_url

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"
DATA_DIR = PROJECT_ROOT / "data"

load_dotenv(PROJECT_ROOT / ".env")


def _database_url() -> URL:
    configured_url = os.getenv("DATABASE_URL")
    if not configured_url:
        raise ValueError("DATABASE_URL debe configurarse en el archivo .env.")

    url = make_url(configured_url)
    if url.get_backend_name() != "postgresql":
        raise ValueError("DATABASE_URL debe apuntar a PostgreSQL.")

    query = dict(url.query)
    ssl_mode = query.pop("sslmode", None)
    if ssl_mode:
        query["ssl"] = ssl_mode

    password = url.password or os.getenv("POSTGRES_DB_PASS")
    if not password:
        raise ValueError(
            "Define la contraseña en DATABASE_URL o en POSTGRES_DB_PASS."
        )

    return url.set(
        drivername="postgresql+asyncpg",
        password=password,
        query=query,
    )


DATABASE_URL = _database_url()

SESSION_SECRET = os.getenv("SESSION_SECRET", "change-this-development-secret")
JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_urlsafe(32)
if not os.getenv("JWT_SECRET"):
    logger.warning(
        "JWT_SECRET is unset; using a temporary process-local signing secret. "
        "Set JWT_SECRET to a stable random value for deployments."
    )

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
