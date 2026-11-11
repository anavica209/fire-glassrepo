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

POSITIONS = (POSITION_PAST, POSITION_PRESENT, POSITION_FUTURE)
POSITION_LABELS = {
    POSITION_PAST: "Lo que te trajo hasta aquí",
    POSITION_PRESENT: "Lo que está vivo ahora",
    POSITION_FUTURE: "Una posibilidad en el horizonte",
}

CATEGORY_TEXT = {
    CATEGORY_LOVE: (
        "Amor y relaciones",
        "En tus relaciones, considera cómo expresar lo que necesitas con honestidad y escuchar también los límites de la otra persona.",
    ),
    CATEGORY_WORK: (
        "Trabajo y finanzas",
        "En tu trabajo y tus recursos, busca un paso concreto que refleje esta idea y respete tus prioridades.",
    ),
    CATEGORY_GROWTH: (
        "Crecimiento personal",
        "En tu proceso personal, explora esta idea con curiosidad y sin exigirte resolverlo todo hoy.",
    ),
    CATEGORY_GENERAL: (
        "Lectura general",
        "En tu día a día, observa dónde aparece esta energía y qué pequeña decisión sí está en tus manos.",
    ),
}

CARD_TEXT = {
    CARD_FOOL: (
        ("Nuevos comienzos", "Espontaneidad", "Confianza"),
        "Se abre una posibilidad inesperada. Puedes avanzar con curiosidad, sin necesitar tener todas las respuestas, y cuidar a la vez aquello que es importante para ti.",
    ),
    CARD_MAGICIAN: (
        ("Iniciativa", "Recursos", "Acción"),
        "Ya cuentas con más herramientas de las que imaginas. Un paso concreto, nacido de tu intención, puede transformar una idea en algo real.",
    ),
    CARD_HIGH_PRIESTESS: (
        ("Intuición", "Silencio", "Sabiduría interior"),
        "Tal vez la respuesta no llegue haciendo más, sino escuchando mejor. Date espacio para observar lo que sientes antes de decidir.",
    ),
    CARD_EMPRESS: (
        ("Cuidado", "Abundancia", "Creatividad"),
        "Algo puede crecer cuando recibe atención paciente. Nutre tus vínculos, tus ideas y también tu propio bienestar.",
    ),
    CARD_EMPEROR: (
        ("Límites", "Estructura", "Estabilidad"),
        "Poner orden puede darte más libertad. Define qué necesitas y construye una base firme desde la que puedas avanzar.",
    ),
    CARD_HIEROPHANT: (
        ("Aprendizaje", "Valores", "Comunidad"),
        "Una conversación, una tradición o una persona de confianza puede ofrecerte otra perspectiva. Quédate con lo que se alinea con tus valores.",
    ),
    CARD_LOVERS: (
        ("Elección", "Conexión", "Coherencia"),
        "Una decisión importante pide honestidad contigo y con los demás. Busca el camino que refleje lo que de verdad valoras.",
    ),
    CARD_CHARIOT: (
        ("Dirección", "Determinación", "Avance"),
        "Hay energía disponible para moverte hacia adelante. Elige un rumbo y procura que tus distintas prioridades trabajen juntas.",
    ),
    CARD_STRENGTH: (
        ("Valentía", "Paciencia", "Compasión"),
        "La firmeza no siempre necesita imponerse. La paciencia y un trato amable hacia ti mismo pueden ser tu mayor fortaleza.",
    ),
    CARD_HERMIT: (
        ("Pausa", "Reflexión", "Claridad"),
        "Tomar distancia por un momento puede ayudarte a distinguir tu propia voz. No es necesario apresurar una respuesta que aún está madurando.",
    ),
    CARD_WHEEL_OF_FORTUNE: (
        ("Cambio", "Ciclos", "Oportunidad"),
        "Las circunstancias cambian y no todo está bajo tu control. Observa qué oportunidad trae este giro y qué sí puedes elegir ahora.",
    ),
    CARD_JUSTICE: (
        ("Equilibrio", "Honestidad", "Consecuencias"),
        "Mira la situación con claridad y considera las necesidades de cada parte. Una decisión coherente puede traer equilibrio, aunque requiera valentía.",
    ),
    CARD_HANGED_MAN: (
        ("Nueva perspectiva", "Pausa", "Soltar"),
        "Quizá avanzar signifique mirar el asunto de otra manera. Permítete pausar y dejar ir aquello que ya no te ayuda.",
    ),
    CARD_DEATH: (
        ("Transformación", "Cierre", "Renovación"),
        "Un ciclo puede estar cambiando de forma. Honrar lo que termina deja espacio para descubrir qué quieres llevar contigo.",
    ),
    CARD_TEMPERANCE: (
        ("Armonía", "Medida", "Integración"),
        "No hace falta resolverlo todo de golpe. Combinar paciencia con pequeños ajustes puede acercarte a un equilibrio sostenible.",
    ),
    CARD_DEVIL: (
        ("Apegos", "Conciencia", "Elección"),
        "Observa con curiosidad qué hábito, miedo o expectativa limita tu margen de acción. Reconocerlo puede abrir nuevas opciones.",
    ),
    CARD_TOWER: (
        ("Cambio repentino", "Verdad", "Reconstrucción"),
        "Una estructura puede estar pidiendo revisión. Aunque el cambio incomode, puedes elegir qué conservar y qué reconstruir de forma más auténtica.",
    ),
    CARD_STAR: (
        ("Esperanza", "Inspiración", "Confianza"),
        "Después de un período intenso, puede volver la sensación de posibilidad. Atiende lo que te devuelve calma y te ayuda a recuperar confianza.",
    ),
    CARD_MOON: (
        ("Emociones", "Incertidumbre", "Escucha"),
        "No todo está claro todavía, y eso está bien. Separa los hechos de los temores y date tiempo para comprender lo que sientes.",
    ),
    CARD_SUN: (
        ("Vitalidad", "Claridad", "Alegría"),
        "Hay espacio para reconocer lo que sí funciona y disfrutarlo sin culpa. La claridad compartida puede fortalecer tus vínculos y proyectos.",
    ),
    CARD_JUDGMENT: (
        ("Despertar", "Revisión", "Renovación"),
        "Una experiencia pasada puede ayudarte a responder de otra manera hoy. Escucha qué cambio te pide tu presente, sin juzgar tu recorrido.",
    ),
    CARD_WORLD: (
        ("Integración", "Logro", "Nuevo ciclo"),
        "Algo importante puede estar llegando a una conclusión. Reconoce cuánto has recorrido y permite que ese cierre abra un comienzo distinto.",
    ),
}
