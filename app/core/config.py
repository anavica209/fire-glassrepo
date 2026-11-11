import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"
DATA_DIR = PROJECT_ROOT / "data"
ANALYTICS_DB_PATH = DATA_DIR / "fire_glass_analytics.db"

load_dotenv(PROJECT_ROOT / ".env")

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
