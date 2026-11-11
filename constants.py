"""Default Spanish copy and catalog data for readings."""

from app_constants import (
    CARD_CHARIOT,
    CARD_DEATH,
    CARD_DEVIL,
    CARD_EMPEROR,
    CARD_EMPRESS,
    CARD_FOOL,
    CARD_HANGED_MAN,
    CARD_HERMIT,
    CARD_HIGH_PRIESTESS,
    CARD_HIEROPHANT,
    CARD_JUDGMENT,
    CARD_JUSTICE,
    CARD_LOVERS,
    CARD_MAGICIAN,
    CARD_MOON,
    CARD_STRENGTH,
    CARD_STAR,
    CARD_SUN,
    CARD_TEMPERANCE,
    CARD_TOWER,
    CARD_WHEEL_OF_FORTUNE,
    CARD_WORLD,
    CATEGORY_GENERAL,
    CATEGORY_GROWTH,
    CATEGORY_LOVE,
    CATEGORY_WORK,
    POSITION_FUTURE,
    POSITION_PAST,
    POSITION_PRESENT,
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
