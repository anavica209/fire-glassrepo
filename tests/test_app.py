from io import BytesIO
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "admin",
            "grant_type": "password",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_home_redirects_to_login_when_signed_out(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_web_login_creates_session(client):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert client.get("/").status_code == 200


def test_token_endpoint_rejects_invalid_credentials(client):
    response = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "incorrect",
            "grant_type": "password",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_reading_requires_authentication(client):
    response = client.post(
        "/api/reading",
        json={"category": "general", "question": "¿Qué necesito tener en cuenta?"},
    )

    assert response.status_code == 401


def test_reading_returns_three_distinct_cards_and_normalizes_question(
    client, auth_headers
):
    response = client.post(
        "/api/reading",
        headers=auth_headers,
        json={"category": "amor", "question": "  ¿Cómo puedo escuchar mejor?  "},
    )

    assert response.status_code == 200
    reading = response.json()
    assert reading["category"] == "amor"
    assert reading["category_label"] == "Amor y relaciones"
    assert reading["question"] == "¿Cómo puedo escuchar mejor?"
    assert [card["position"] for card in reading["cards"]] == [
        "Pasado",
        "Presente",
        "Lo que viene",
    ]
    assert len({card["name"] for card in reading["cards"]}) == 3
    assert all(card["keywords"] and card["interpretation"] for card in reading["cards"])


def test_reading_rejects_unknown_category(client, auth_headers):
    response = client.post(
        "/api/reading",
        headers=auth_headers,
        json={"category": "unknown", "question": ""},
    )

    assert response.status_code == 422


def test_download_rejects_repeated_cards(client, auth_headers):
    response = client.post(
        "/api/reading/download",
        headers=auth_headers,
        json={
            "category": "general",
            "cards": [
                {"position": "Pasado", "name": "El Loco"},
                {"position": "Presente", "name": "El Loco"},
                {"position": "Lo que viene", "name": "El Mundo"},
            ],
        },
    )

    assert response.status_code == 422


def test_download_returns_zip_with_one_svg_per_card(client, auth_headers):
    response = client.post(
        "/api/reading/download",
        headers=auth_headers,
        json={
            "category": "general",
            "cards": [
                {"position": "Pasado", "name": "El Loco"},
                {"position": "Presente", "name": "El Mago"},
                {"position": "Lo que viene", "name": "El Mundo"},
            ],
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert 'filename="lectura-fire-glass.zip"' in response.headers["content-disposition"]
    with ZipFile(BytesIO(response.content)) as archive:
        assert archive.namelist() == [
            "carta-1-pasado.svg",
            "carta-2-presente.svg",
            "carta-3-lo-que-viene.svg",
        ]
        assert all(archive.read(name).startswith(b"<svg ") for name in archive.namelist())
