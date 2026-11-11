from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import core
import main
import routers.analytics as analytics


@pytest.fixture
def client():
    core.active_section_sessions.clear()
    with TestClient(main.app) as test_client:
        yield test_client
    core.active_section_sessions.clear()


def sign_in_as_admin(client):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_section_tracking_requires_a_signed_in_user(client):
    response = client.post(
        "/api/analytics/section",
        json={"session_id": str(uuid4()), "section": 1},
    )

    assert response.status_code == 401


def test_section_tracking_persists_duration_when_session_ends(client, monkeypatch):
    record = MagicMock(
        user_key=None,
        username=None,
        section=None,
        duration_seconds=None,
    )

    def save_duration(user_key, username, section, duration_seconds):
        record.user_key = user_key
        record.username = username
        record.section = section
        record.duration_seconds = duration_seconds

    save_duration_mock = MagicMock(side_effect=save_duration)
    monkeypatch.setattr(main, "save_section_duration", save_duration_mock)
    sign_in_as_admin(client)
    session_id = str(uuid4())

    started = client.post(
        "/api/analytics/section",
        json={"session_id": session_id, "section": 1},
    )
    ended = client.post(
        "/api/analytics/section",
        json={"session_id": session_id, "section": None},
    )

    assert started.status_code == 204
    assert ended.status_code == 204
    save_duration_mock.assert_called_once_with(
        record.user_key,
        record.username,
        record.section,
        record.duration_seconds,
    )
    assert record.user_key != "admin@example.com"
    assert record.username == "Admin"
    assert record.section == 1
    assert record.duration_seconds > 0


def test_analytics_page_shows_aggregated_times_to_admin(client, monkeypatch, tmp_path):
    database_path = tmp_path / "analytics.db"
    monkeypatch.setattr(core, "ANALYTICS_DB_PATH", database_path)
    monkeypatch.setattr(analytics, "ANALYTICS_DB_PATH", database_path)
    core.save_section_duration("hashed-user", "Ana", 1, 65.6)
    core.save_section_duration("hashed-user", "Ana", 2, 123.4)
    sign_in_as_admin(client)

    response = client.get("/analytics")

    assert response.status_code == 200
    assert "Ana" in response.text
    assert "1 min 5 s" in response.text
    assert "2 min 3 s" in response.text


def test_analytics_page_requires_a_signed_in_user(client):
    response = client.get("/analytics")

    assert response.status_code == 401
