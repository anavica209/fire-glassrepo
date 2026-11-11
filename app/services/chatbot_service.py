import logging
import re
import textwrap
from typing import Any

import httpx

from app.core.config import GROQ_API_KEY
from app.services.pdf_ingest import find_relevant_passages

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Eres la guía de tarot de Fire glass: cercana, serena y clara. Responde en español.
Ayuda a comprender nociones básicas del tarot, los arcanos y sus símbolos, y a
reflexionar sobre las lecturas sin presentar sus interpretaciones como hechos,
predicciones seguras ni sustitutos de decisiones personales.

En una tirada de tres cartas, explica que el pasado señala experiencias o
patrones que influyen en la situación; el presente invita a observar lo que está
activo ahora; y el futuro representa una posibilidad o tendencia abierta, no un
destino inevitable. Relaciona las posiciones entre sí cuando sea útil.
Si el usuario pregunta cómo empezar, sugiere formular una pregunta abierta,
barajar pensando en ella y leer cada carta en el contexto de su posición.
Usa el material de referencia cuando sea pertinente y no inventes citas ni
afirmes que conoces cartas que el usuario no ha mencionado.

Responde de forma concisa en un máximo de cinco líneas cortas (hasta 44
caracteres por línea). Prioriza la respuesta directa y evita explicaciones
largas o enumeraciones extensas. Si hay otro tema útil que no alcances a tratar,
reserva la última línea para sugerirlo como pregunta concreta. No agregues una
introducción ni una conclusión que repitan la respuesta.
"""

CHAT_API_URL = "https://api.groq.com/openai/v1/chat/completions"
CHAT_MODEL = "openai/gpt-oss-20b"
MAX_REPLY_LINES = 5
MAX_REPLY_LINE_LENGTH = 44
FOLLOW_UP_LINE = "Pregúntame por otro tema si quieres."
OVERLONG_SENTENCE_LINE = "Puedo explicarlo por partes."


def _format_reply(content: str) -> str:
    normalized = " ".join(content.split())

    def wrap_sentence(sentence: str) -> list[str]:
        return textwrap.wrap(
            sentence,
            width=MAX_REPLY_LINE_LENGTH,
            break_long_words=True,
            break_on_hyphens=False,
        )

    lines = wrap_sentence(normalized)
    if len(lines) <= MAX_REPLY_LINES:
        return "\n".join(lines)

    answer_lines = []
    for sentence in re.split(r"(?<=[.!?])\s+", normalized):
        sentence_lines = wrap_sentence(sentence)
        if len(answer_lines) + len(sentence_lines) > MAX_REPLY_LINES - 1:
            break
        answer_lines.extend(sentence_lines)

    if not answer_lines:
        answer_lines.append(OVERLONG_SENTENCE_LINE)
    answer_lines.append(FOLLOW_UP_LINE)
    lines = answer_lines
    return "\n".join(lines)


def invoke_chatbot(messages: list[dict[str, str]]) -> str:
    api_key = GROQ_API_KEY
    if not api_key:
        raise RuntimeError(
            "El chat todavía no está configurado. Añade GROQ_API_KEY al archivo .env."
        )

    context = find_relevant_passages(messages[-1]["content"])
    system_prompt = SYSTEM_PROMPT
    if context:
        system_prompt += f"\n\nMaterial de referencia de la guía de tarot:\n{context}"

    payload: dict[str, Any] = {
        "model": CHAT_MODEL,
        "temperature": 0.4,
        "reasoning_effort": "low",
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        "max_completion_tokens": 1024,
    }

    try:
        response = httpx.post(
            CHAT_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        provider_error = {}
        try:
            response_body = exc.response.json()
        except ValueError:
            response_body = {}
        if isinstance(response_body, dict):
            candidate = response_body.get("error")
            if isinstance(candidate, dict):
                provider_error = candidate

        provider_code = provider_error.get("code") or provider_error.get("type")
        provider_message = provider_error.get("message")
        if not isinstance(provider_message, str):
            provider_message = ""
        provider_message = " ".join(provider_message.split())[:300]
        logger.error(
            "Tarot chat provider returned status=%s code=%s message=%s",
            exc.response.status_code,
            provider_code or "unknown",
            provider_message or "No error message provided.",
        )
        if exc.response.status_code == 404:
            detail = (
                "Groq respondió con error 404. Consulta el mensaje detallado del "
                "proveedor en la terminal para identificar qué recurso no encontró."
            )
        else:
            detail = (
                f"Groq rechazó la solicitud (HTTP {exc.response.status_code}). "
                "Consulta el mensaje detallado del proveedor en la terminal."
            )
        raise RuntimeError(
            detail
        ) from exc
    except httpx.RequestError as exc:
        logger.exception("Could not reach the tarot chat provider.")
        raise RuntimeError(
            "No pudimos conectar con el chat. Comprueba tu conexión e inténtalo de nuevo."
        ) from exc

    try:
        result = response.json()
    except ValueError as exc:
        logger.exception("Tarot chat provider returned invalid JSON.")
        raise RuntimeError("El chat devolvió una respuesta inválida.") from exc

    choices = result.get("choices") if isinstance(result, dict) else None
    choice = choices[0] if isinstance(choices, list) and choices else None
    message = choice.get("message") if isinstance(choice, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        finish_reason = choice.get("finish_reason") if isinstance(choice, dict) else None
        logger.error(
            "Tarot chat provider returned no message content finish_reason=%s",
            finish_reason or "unknown",
        )
        if finish_reason == "length":
            raise RuntimeError(
                "Groq agotó el límite de generación antes de terminar la respuesta. "
                "Inténtalo de nuevo."
            )
        raise RuntimeError(
            "Groq no generó texto para esta respuesta. Inténtalo de nuevo."
        )

    return _format_reply(content.strip())
