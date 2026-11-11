"""Tests for analytics tracking and admin reporting."""

# pylint: disable=redefined-outer-name  # Pytest injects fixtures as test parameters.

import re
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import main
import routers.analytics as analytics
from core import active_section_sessions


@pytest.fixture(name="client")
def client_fixture():
    "Return a client"
    active_section_sessions.clear()
    with TestClient(main.app) as test_client:
        yield test_client
    active_section_sessions.clear()


def sign_in_as_admin(client):
    "Login as admin and redirect (required for authorized operations)"
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert response.status_code == 303


def mock_analytics_records(monkeypatch, records):
    """Provide report rows as ordinary Python objects."""
    records_mock = MagicMock(return_value=records)
    monkeypatch.setattr(analytics, "_load_analytics_records", records_mock)
    return records_mock


def test_section_tracking_requires_a_signed_in_user(client):
    "Fail to access the resource if the user is not signed in"
    response = client.post(
        "/api/analytics/section",
        json={"session_id": str(uuid4()), "section": 1},
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "flow_step",
    range(1, 6),
    ids=[f"step-{step}" for step in range(1, 6)],
)
def test_flow_step_tracking_persists_duration_when_step_ends(
    client, monkeypatch, flow_step
):
    "Simulate steps calls and validate time tracking between flow steps"
    record = MagicMock(
        user_key=None,
        username=None,
        section=None,
        duration_seconds=None,
    )

    def save_duration(user_key, username, section, duration_seconds):
        "save the values in the record once the call is intercepted"
        record.user_key = user_key
        record.username = username
        record.section = section
        record.duration_seconds = duration_seconds

    save_duration_mock = MagicMock(side_effect=save_duration)
    monkeypatch.setattr(main, "save_section_duration", save_duration_mock)
    sign_in_as_admin(client)
    session_id = str(uuid4())

    # init the timer 
    started = client.post(
        "/api/analytics/section",
        json={"session_id": session_id, "section": flow_step},
    )
    # makes the middleware to calculate how much time has passed
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
    assert record.section == flow_step
    assert record.duration_seconds > 0


@pytest.mark.parametrize(
    ("step_number", "flow_step_label", "formatted_duration"),
    [
        pytest.param(1, "Bienvenida", "1 min 5 s", id="step-1"),
        pytest.param(2, "Enfoque", "2 min 3 s", id="step-2"),
        pytest.param(3, "El encuentro", "3 min 0 s", id="step-3"),
        pytest.param(4, "Tu lectura", "4 min 5 s", id="step-4"),
        pytest.param(5, "Integrar", "5 min 5 s", id="step-5"),
    ],
)
def test_analytics_page_shows_aggregated_times_to_admin(
    client, monkeypatch, step_number, flow_step_label, formatted_duration
):
    "Verifies that the admin report shows accumulated time for each flow step"
    records_mock = mock_analytics_records(
        monkeypatch,
        [
            {
                "username": "Ana",
                "section_1": 65.6,
                "section_2": 123.4,
                "section_3": 180,
                "section_4": 245,
                "section_5": 305,
            }
        ],
    )
    sign_in_as_admin(client)

    response = client.get("/analytics")

    assert response.status_code == 200
    assert "Ana" in response.text
    assert re.search(
        rf'<td data-label="Paso {step_number} · {flow_step_label}">\s*'
        rf"<strong>{re.escape(formatted_duration)}</strong>",
        response.text,
    )
    records_mock.assert_called_once_with()


def test_analytics_page_does_not_track_time_for_the_admin_page(client, monkeypatch):
    "Confirms viewing the admin report does not start flow-step time tracking"
    records_mock = mock_analytics_records(monkeypatch, [])
    sign_in_as_admin(client)

    response = client.get("/analytics")

    assert response.status_code == 200
    assert not active_section_sessions
    records_mock.assert_called_once_with()


def test_analytics_page_requires_a_signed_in_user(client):
    "Only access analytics if logged in"
    response = client.get("/analytics")

    assert response.status_code == 401
