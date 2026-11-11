import logging

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.constants import (
    DEMO_PASSWORD,
    DEMO_USERNAME,
    FIELD_ACCESS_TOKEN,
    FIELD_GRANT_TYPE,
    FIELD_PASSWORD,
    FIELD_USERNAME,
    GRANT_TYPE_PASSWORD,
)
from app.main import app
from app.services import chatbot_service
from app.services.chatbot_service import _format_reply, invoke_chatbot


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/auth/token",
        data={
            FIELD_USERNAME: DEMO_USERNAME,
            FIELD_PASSWORD: DEMO_PASSWORD,
            FIELD_GRANT_TYPE: GRANT_TYPE_PASSWORD,
        },
    )
    assert response.status_code == 200
    return {
        "Authorization": f"Bearer {response.json()[FIELD_ACCESS_TOKEN]}"
    }


def test_chat_requires_authentication(client):
    response = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "¿Qué significa el tarot?"}]},
    )

    assert response.status_code == 401


def test_chat_returns_reply_for_authenticated_user(client, auth_headers, monkeypatch):
    received_messages = []

    def fake_invoke_chatbot(messages):
        received_messages.extend(messages)
        return "El pasado señala experiencias que influyen en el presente."

    monkeypatch.setattr("app.api.chat.invoke_chatbot", fake_invoke_chatbot)
    response = client.post(
        "/api/chat",
        headers=auth_headers,
        json={
            "messages": [
                {"role": "user", "content": "¿Cómo se lee una tirada?"},
                {"role": "assistant", "content": "Se interpreta cada carta."},
                {"role": "user", "content": "¿Y el pasado?"},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "reply": "El pasado señala experiencias que influyen en el presente."
    }
    assert received_messages[-1] == {"role": "user", "content": "¿Y el pasado?"}


def test_chat_provider_error_logs_diagnostic_without_api_key(monkeypatch, caplog):
    api_key = "test-key-not-for-logging"
    monkeypatch.setattr(chatbot_service, "GROQ_API_KEY", api_key)
    monkeypatch.setattr(chatbot_service, "find_relevant_passages", lambda _query: "")
    response = httpx.Response(
        404,
        json={"error": {"message": "Route not found", "type": "invalid_request_error"}},
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
    )
    monkeypatch.setattr(chatbot_service.httpx, "post", lambda *_args, **_kwargs: response)

    with caplog.at_level(logging.ERROR, logger="app.services.chatbot_service"):
        with pytest.raises(RuntimeError, match="404"):
            invoke_chatbot([{"role": "user", "content": "¿Qué significa el pasado?"}])

    assert "Route not found" in caplog.text
    assert api_key not in caplog.text


def test_chat_uses_available_groq_model(monkeypatch):
    monkeypatch.setattr(chatbot_service, "GROQ_API_KEY", "test-key-not-for-network")
    monkeypatch.setattr(chatbot_service, "find_relevant_passages", lambda _query: "")
    captured_request = {}

    def fake_post(url, *, headers, json, timeout):
        captured_request.update(url=url, headers=headers, payload=json, timeout=timeout)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "El pasado aporta contexto."}}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(chatbot_service.httpx, "post", fake_post)
    reply = invoke_chatbot(
        [{"role": "user", "content": "¿Qué representa el pasado?"}]
    )

    assert reply == "El pasado aporta contexto."
    assert captured_request["payload"]["model"] == "openai/gpt-oss-20b"
    assert captured_request["payload"]["reasoning_effort"] == "low"
    assert captured_request["payload"]["max_completion_tokens"] == 1024
    assert captured_request["headers"]["Authorization"] == (
        "Bearer test-key-not-for-network"
    )


def test_chat_explains_empty_provider_response_from_token_limit(monkeypatch, caplog):
    monkeypatch.setattr(chatbot_service, "GROQ_API_KEY", "test-key-not-for-network")
    monkeypatch.setattr(chatbot_service, "find_relevant_passages", lambda _query: "")
    response = httpx.Response(
        200,
        json={"choices": [{"message": {"content": ""}, "finish_reason": "length"}]},
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
    )
    monkeypatch.setattr(chatbot_service.httpx, "post", lambda *_args, **_kwargs: response)

    with caplog.at_level(logging.ERROR, logger="app.services.chatbot_service"):
        with pytest.raises(RuntimeError, match="agotó el límite"):
            invoke_chatbot([{"role": "user", "content": "¿Qué representa el pasado?"}])

    assert "finish_reason=length" in caplog.text


def test_chat_reply_is_limited_to_five_short_lines():
    reply = _format_reply(" ".join(["tarot"] * 100))
    lines = reply.splitlines()

    assert len(lines) == 2
    assert all(len(line) <= 44 for line in lines)
    assert lines[0] == "Puedo explicarlo por partes."
    assert lines[-1] == "Pregúntame por otro tema si quieres."


def test_chat_reply_truncates_only_after_complete_sentences():
    response = (
        "El pasado influye en el presente. "
        + "Esta carta señala aprendizajes que vale la pena observar con calma. " * 8
    )
    lines = _format_reply(response).splitlines()

    assert len(lines) <= 5
    assert lines[-1] == "Pregúntame por otro tema si quieres."
    assert "\n".join(lines[:-1]).rstrip().endswith(".")
