"""Shared application identifiers, demo data, and API field names."""

from typing import Final

FIELD_USERNAME: Final = "username"
FIELD_PASSWORD: Final = "password"
FIELD_GRANT_TYPE: Final = "grant_type"
FIELD_ACCESS_TOKEN: Final = "access_token"
FIELD_TOKEN_TYPE: Final = "token_type"
FIELD_SUBJECT: Final = "sub"
FIELD_DETAIL: Final = "detail"
FIELD_EMAIL: Final = "email"
FIELD_ROLE: Final = "role"
FIELD_USER_KEY: Final = "user_key"
FIELD_USER: Final = "user"
FIELD_CATEGORY: Final = "category"
FIELD_CATEGORY_LABEL: Final = "category_label"
FIELD_CATEGORY_FOCUS: Final = "category_focus"
FIELD_QUESTION: Final = "question"
FIELD_CARDS: Final = "cards"
FIELD_POSITION: Final = "position"
FIELD_POSITION_LABEL: Final = "position_label"
FIELD_NAME: Final = "name"
FIELD_KEYWORDS: Final = "keywords"
FIELD_INTERPRETATION: Final = "interpretation"
FIELD_SESSION_ID: Final = "session_id"
FIELD_SECTION: Final = "section"
FIELD_STARTED_AT: Final = "started_at"
FIELD_SECTION_TRACKING: Final = "section_tracking"
FIELD_ADMIN: Final = "admin"
FIELD_ROWS: Final = "rows"
FIELD_DURATIONS: Final = "durations"
FIELD_LABEL: Final = "label"
FIELD_SECONDS: Final = "seconds"
FIELD_FORMATTED: Final = "formatted"

API_FIELDS: Final = {
    "accessToken": FIELD_ACCESS_TOKEN,
    "cards": FIELD_CARDS,
    "category": FIELD_CATEGORY,
    "categoryFocus": FIELD_CATEGORY_FOCUS,
    "categoryLabel": FIELD_CATEGORY_LABEL,
    "detail": FIELD_DETAIL,
    "interpretation": FIELD_INTERPRETATION,
    "keywords": FIELD_KEYWORDS,
    "name": FIELD_NAME,
    "position": FIELD_POSITION,
    "positionLabel": FIELD_POSITION_LABEL,
    "question": FIELD_QUESTION,
    "section": FIELD_SECTION,
    "sessionId": FIELD_SESSION_ID,
}

DEMO_USERNAME: Final = "admin"
DEMO_PASSWORD: Final = "admin"
DEMO_DISPLAY_NAME: Final = "Admin"
DEMO_EMAIL: Final = "admin@example.com"
ADMIN_ROLE: Final = "admin"
INVALID_PASSWORD: Final = "incorrect"
INVALID_CATEGORY: Final = "unknown"
GRANT_TYPE_PASSWORD: Final = "password"

CATEGORY_LOVE: Final = "amor"
CATEGORY_WORK: Final = "trabajo"
CATEGORY_GROWTH: Final = "crecimiento"
CATEGORY_GENERAL: Final = "general"
DEFAULT_CATEGORY: Final = CATEGORY_LOVE
CATEGORY_IDS: Final = {
    "love": CATEGORY_LOVE,
    "work": CATEGORY_WORK,
    "growth": CATEGORY_GROWTH,
    "general": CATEGORY_GENERAL,
}

POSITION_PAST: Final = "Pasado"
POSITION_PRESENT: Final = "Presente"
POSITION_FUTURE: Final = "Lo que viene"

CARD_FOOL: Final = "El Loco"
CARD_MAGICIAN: Final = "El Mago"
CARD_HIGH_PRIESTESS: Final = "La Sacerdotisa"
CARD_EMPRESS: Final = "La Emperatriz"
CARD_EMPEROR: Final = "El Emperador"
CARD_HIEROPHANT: Final = "El Hierofante"
CARD_LOVERS: Final = "Los Enamorados"
CARD_CHARIOT: Final = "El Carro"
CARD_STRENGTH: Final = "La Fuerza"
CARD_HERMIT: Final = "El Ermitaño"
CARD_WHEEL_OF_FORTUNE: Final = "La Rueda de la Fortuna"
CARD_JUSTICE: Final = "La Justicia"
CARD_HANGED_MAN: Final = "El Colgado"
CARD_DEATH: Final = "La Muerte"
CARD_TEMPERANCE: Final = "La Templanza"
CARD_DEVIL: Final = "El Diablo"
CARD_TOWER: Final = "La Torre"
CARD_STAR: Final = "La Estrella"
CARD_MOON: Final = "La Luna"
CARD_SUN: Final = "El Sol"
CARD_JUDGMENT: Final = "El Juicio"
CARD_WORLD: Final = "El Mundo"

SAMPLE_QUESTION: Final = "¿Cómo puedo escuchar mejor?"
GENERAL_QUESTION: Final = "¿Qué necesito tener en cuenta?"
SAMPLE_ANALYTICS_USERNAME: Final = "Ana"

SAMPLE_CARDS = (
    {FIELD_POSITION: POSITION_PAST, FIELD_NAME: CARD_FOOL},
    {FIELD_POSITION: POSITION_PRESENT, FIELD_NAME: CARD_MAGICIAN},
    {FIELD_POSITION: POSITION_FUTURE, FIELD_NAME: CARD_WORLD},
)
