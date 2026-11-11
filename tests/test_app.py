from io import BytesIO
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from app_constants import (
    CATEGORY_GENERAL,
    CATEGORY_LOVE,
    DEMO_PASSWORD,
    DEMO_USERNAME,
    FIELD_ACCESS_TOKEN,
    FIELD_CARDS,
    FIELD_CATEGORY,
    FIELD_CATEGORY_LABEL,
    FIELD_GRANT_TYPE,
    FIELD_INTERPRETATION,
    FIELD_KEYWORDS,
    FIELD_NAME,
    FIELD_PASSWORD,
    FIELD_POSITION,
    FIELD_QUESTION,
    FIELD_USERNAME,
    GRANT_TYPE_PASSWORD,
    GENERAL_QUESTION,
    INVALID_CATEGORY,
    INVALID_PASSWORD,
    POSITION_PRESENT,
    SAMPLE_CARDS,
    SAMPLE_QUESTION,
)
from constants import POSITIONS, CATEGORY_TEXT
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
            FIELD_USERNAME: DEMO_USERNAME,
            FIELD_PASSWORD: DEMO_PASSWORD,
            FIELD_GRANT_TYPE: GRANT_TYPE_PASSWORD,
        },
    )
    assert response.status_code == 200
    return {
        "Authorization": f"Bearer {response.json()[FIELD_ACCESS_TOKEN]}"
    }


def test_home_redirects_to_login_when_signed_out(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_web_login_creates_session(client):
    response = client.post(
        "/auth/login",
        data={
            FIELD_USERNAME: DEMO_USERNAME,
            FIELD_PASSWORD: DEMO_PASSWORD,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert client.get("/").status_code == 200


def test_token_endpoint_rejects_invalid_credentials(client):
    response = client.post(
        "/auth/token",
        data={
            FIELD_USERNAME: DEMO_USERNAME,
            FIELD_PASSWORD: INVALID_PASSWORD,
            FIELD_GRANT_TYPE: GRANT_TYPE_PASSWORD,
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_reading_requires_authentication(client):
    response = client.post(
        "/api/reading",
        json={
            FIELD_CATEGORY: CATEGORY_GENERAL,
            FIELD_QUESTION: GENERAL_QUESTION,
        },
    )

    assert response.status_code == 401


def test_reading_returns_three_distinct_cards_and_normalizes_question(
    client, auth_headers
):
    response = client.post(
        "/api/reading",
        headers=auth_headers,
        json={
            FIELD_CATEGORY: CATEGORY_LOVE,
            FIELD_QUESTION: f"  {SAMPLE_QUESTION}  ",
        },
    )

    assert response.status_code == 200
    reading = response.json()
    assert reading[FIELD_CATEGORY] == CATEGORY_LOVE
    assert reading[FIELD_CATEGORY_LABEL] == CATEGORY_TEXT[CATEGORY_LOVE][0]
    assert reading[FIELD_QUESTION] == SAMPLE_QUESTION
    assert [
        card[FIELD_POSITION] for card in reading[FIELD_CARDS]
    ] == list(POSITIONS)
    assert len({card[FIELD_NAME] for card in reading[FIELD_CARDS]}) == 3
    assert all(
        card[FIELD_KEYWORDS] and card[FIELD_INTERPRETATION]
        for card in reading[FIELD_CARDS]
    )


def test_reading_rejects_unknown_category(client, auth_headers):
    response = client.post(
        "/api/reading",
        headers=auth_headers,
        json={FIELD_CATEGORY: INVALID_CATEGORY, FIELD_QUESTION: ""},
    )

    assert response.status_code == 422


def test_download_rejects_repeated_cards(client, auth_headers):
    response = client.post(
        "/api/reading/download",
        headers=auth_headers,
        json={
            FIELD_CATEGORY: CATEGORY_GENERAL,
            FIELD_CARDS: [
                SAMPLE_CARDS[0],
                {
                    FIELD_POSITION: POSITION_PRESENT,
                    FIELD_NAME: SAMPLE_CARDS[0][FIELD_NAME],
                },
                SAMPLE_CARDS[2],
            ],
        },
    )

    assert response.status_code == 422


def test_download_returns_zip_with_one_svg_per_card(client, auth_headers):
    response = client.post(
        "/api/reading/download",
        headers=auth_headers,
        json={
            FIELD_CATEGORY: CATEGORY_GENERAL,
            FIELD_CARDS: SAMPLE_CARDS,
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert 'filename="lectura-fire-glass.zip"' in response.headers["content-disposition"]
    with ZipFile(BytesIO(response.content)) as archive:
        assert archive.namelist() == [
            f"carta-{index}-{card[FIELD_POSITION].lower().replace(' ', '-')}.svg"
            for index, card in enumerate(SAMPLE_CARDS, start=1)
        ]
        assert all(archive.read(name).startswith(b"<svg ") for name in archive.namelist())
