import logging
import os
import secrets
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Literal, TypedDict
from uuid import UUID

import jwt
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
ANALYTICS_DB_PATH = BASE_DIR / "fire_glass_analytics.db"
load_dotenv(BASE_DIR / ".env")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-this-development-secret")
JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_urlsafe(32)
if not os.getenv("JWT_SECRET"):
    logger.warning(
        "JWT_SECRET is unset; using a temporary process-local signing secret. "
        "Set JWT_SECRET to a stable random value for deployments."
    )
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

templates = Jinja2Templates(directory=BASE_DIR / "templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

oauth = OAuth()
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
if google_client_id and google_client_secret:
    oauth.register(
        name="google",
        client_id=google_client_id,
        client_secret=google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

MAJOR_ARCANA = [
    "El Loco",
    "El Mago",
    "La Sacerdotisa",
    "La Emperatriz",
    "El Emperador",
    "El Hierofante",
    "Los Enamorados",
    "El Carro",
    "La Fuerza",
    "El Ermitaño",
    "La Rueda de la Fortuna",
    "La Justicia",
    "El Colgado",
    "La Muerte",
    "La Templanza",
    "El Diablo",
    "La Torre",
    "La Estrella",
    "La Luna",
    "El Sol",
    "El Juicio",
    "El Mundo",
]
POSITIONS = ["Pasado", "Presente", "Lo que viene"]
POSITION_LABELS = {
    "Pasado": "Lo que te trajo hasta aquí",
    "Presente": "Lo que está vivo ahora",
    "Lo que viene": "Una posibilidad en el horizonte",
}
CATEGORIES = {
    "amor": "Amor y relaciones",
    "trabajo": "Trabajo y finanzas",
    "crecimiento": "Crecimiento personal",
    "general": "Lectura general",
}
CATEGORY_FOCUS = {
    "amor": "En tus relaciones, considera cómo expresar lo que necesitas con honestidad y escuchar también los límites de la otra persona.",
    "trabajo": "En tu trabajo y tus recursos, busca un paso concreto que refleje esta idea y respete tus prioridades.",
    "crecimiento": "En tu proceso personal, explora esta idea con curiosidad y sin exigirte resolverlo todo hoy.",
    "general": "En tu día a día, observa dónde aparece esta energía y qué pequeña decisión sí está en tus manos.",
}
CARD_MEANINGS = {
    "El Loco": (["Nuevos comienzos", "Espontaneidad", "Confianza"], "Se abre una posibilidad inesperada. Puedes avanzar con curiosidad, sin necesitar tener todas las respuestas, y cuidar a la vez aquello que es importante para ti."),
    "El Mago": (["Iniciativa", "Recursos", "Acción"], "Ya cuentas con más herramientas de las que imaginas. Un paso concreto, nacido de tu intención, puede transformar una idea en algo real."),
    "La Sacerdotisa": (["Intuición", "Silencio", "Sabiduría interior"], "Tal vez la respuesta no llegue haciendo más, sino escuchando mejor. Date espacio para observar lo que sientes antes de decidir."),
    "La Emperatriz": (["Cuidado", "Abundancia", "Creatividad"], "Algo puede crecer cuando recibe atención paciente. Nutre tus vínculos, tus ideas y también tu propio bienestar."),
    "El Emperador": (["Límites", "Estructura", "Estabilidad"], "Poner orden puede darte más libertad. Define qué necesitas y construye una base firme desde la que puedas avanzar."),
    "El Hierofante": (["Aprendizaje", "Valores", "Comunidad"], "Una conversación, una tradición o una persona de confianza puede ofrecerte otra perspectiva. Quédate con lo que se alinea con tus valores."),
    "Los Enamorados": (["Elección", "Conexión", "Coherencia"], "Una decisión importante pide honestidad contigo y con los demás. Busca el camino que refleje lo que de verdad valoras."),
    "El Carro": (["Dirección", "Determinación", "Avance"], "Hay energía disponible para moverte hacia adelante. Elige un rumbo y procura que tus distintas prioridades trabajen juntas."),
    "La Fuerza": (["Valentía", "Paciencia", "Compasión"], "La firmeza no siempre necesita imponerse. La paciencia y un trato amable hacia ti mismo pueden ser tu mayor fortaleza."),
    "El Ermitaño": (["Pausa", "Reflexión", "Claridad"], "Tomar distancia por un momento puede ayudarte a distinguir tu propia voz. No es necesario apresurar una respuesta que aún está madurando."),
    "La Rueda de la Fortuna": (["Cambio", "Ciclos", "Oportunidad"], "Las circunstancias cambian y no todo está bajo tu control. Observa qué oportunidad trae este giro y qué sí puedes elegir ahora."),
    "La Justicia": (["Equilibrio", "Honestidad", "Consecuencias"], "Mira la situación con claridad y considera las necesidades de cada parte. Una decisión coherente puede traer equilibrio, aunque requiera valentía."),
    "El Colgado": (["Nueva perspectiva", "Pausa", "Soltar"], "Quizá avanzar signifique mirar el asunto de otra manera. Permítete pausar y dejar ir aquello que ya no te ayuda."),
    "La Muerte": (["Transformación", "Cierre", "Renovación"], "Un ciclo puede estar cambiando de forma. Honrar lo que termina deja espacio para descubrir qué quieres llevar contigo."),
    "La Templanza": (["Armonía", "Medida", "Integración"], "No hace falta resolverlo todo de golpe. Combinar paciencia con pequeños ajustes puede acercarte a un equilibrio sostenible."),
    "El Diablo": (["Apegos", "Conciencia", "Elección"], "Observa con curiosidad qué hábito, miedo o expectativa limita tu margen de acción. Reconocerlo puede abrir nuevas opciones."),
    "La Torre": (["Cambio repentino", "Verdad", "Reconstrucción"], "Una estructura puede estar pidiendo revisión. Aunque el cambio incomode, puedes elegir qué conservar y qué reconstruir de forma más auténtica."),
    "La Estrella": (["Esperanza", "Inspiración", "Confianza"], "Después de un período intenso, puede volver la sensación de posibilidad. Atiende lo que te devuelve calma y te ayuda a recuperar confianza."),
    "La Luna": (["Emociones", "Incertidumbre", "Escucha"], "No todo está claro todavía, y eso está bien. Separa los hechos de los temores y date tiempo para comprender lo que sientes."),
    "El Sol": (["Vitalidad", "Claridad", "Alegría"], "Hay espacio para reconocer lo que sí funciona y disfrutarlo sin culpa. La claridad compartida puede fortalecer tus vínculos y proyectos."),
    "El Juicio": (["Despertar", "Revisión", "Renovación"], "Una experiencia pasada puede ayudarte a responder de otra manera hoy. Escucha qué cambio te pide tu presente, sin juzgar tu recorrido."),
    "El Mundo": (["Integración", "Logro", "Nuevo ciclo"], "Algo importante puede estar llegando a una conclusión. Reconoce cuánto has recorrido y permite que ese cierre abra un comienzo distinto."),
}


class ReadingRequest(BaseModel):
    category: Literal["amor", "trabajo", "crecimiento", "general"]
    question: str = Field(default="", max_length=500)


class ReadingCard(BaseModel):
    position: Literal["Pasado", "Presente", "Lo que viene"]
    name: str

    @model_validator(mode="after")
    def validate_card_name(self):
        if self.name not in MAJOR_ARCANA:
            raise ValueError("La lectura contiene una carta no reconocida.")
        return self


class DownloadReadingRequest(BaseModel):
    category: Literal["amor", "trabajo", "crecimiento", "general"]
    cards: list[ReadingCard] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def validate_cards(self):
        if [card.position for card in self.cards] != POSITIONS:
            raise ValueError("La lectura debe incluir las tres posiciones en orden.")
        if len({card.name for card in self.cards}) != len(self.cards):
            raise ValueError("La lectura no puede repetir cartas.")
        return self


class SectionTrackingRequest(BaseModel):
    session_id: UUID
    section: int | None = Field(default=None, ge=1, le=5)


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
    user = request.session.get("user")
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
    if user.get("role") != "admin" or user.get("email") != "admin@example.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analytics está disponible solo para el usuario administrador.",
        )
    return user




def create_access_token(user: dict[str, str]) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": user["email"],
            "email": user["email"],
            "name": user["name"],
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
        email = payload.get("email")
        name = payload.get("name")
        subject = payload.get("sub")
        if (
            not all(isinstance(value, str) and value for value in (email, name, subject))
            or subject != email
        ):
            raise unauthorized
        return {"email": email, "name": name}
    except jwt.InvalidTokenError as exc:
        raise unauthorized from exc
