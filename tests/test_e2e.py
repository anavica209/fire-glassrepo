"""End-to-end tests for complete user journeys through the application."""

import html
import json
import re
from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from app_constants import (
    API_FIELDS,
    CATEGORY_LOVE,
    DEMO_PASSWORD,
    DEMO_USERNAME,
    FIELD_ACCESS_TOKEN,
    FIELD_CARDS,
    FIELD_CATEGORY,
    FIELD_NAME,
    FIELD_POSITION,
    FIELD_QUESTION,
    FIELD_PASSWORD,
    FIELD_USERNAME,
    SAMPLE_QUESTION,
)
from main import app


def test_user_completes_a_reading_and_downloads_the_cards():
    with TestClient(app) as client:
        login_page = client.get("/login")
        assert login_page.status_code == 200
        assert 'action="/auth/login"' in login_page.text

        login_response = client.post(
            "/auth/login",
            data={
                FIELD_USERNAME: DEMO_USERNAME,
                FIELD_PASSWORD: DEMO_PASSWORD,
            },
            follow_redirects=False,
        )
        assert login_response.status_code == 303
        assert login_response.headers["location"] == "/"

        dashboard = client.get("/")
        assert dashboard.status_code == 200
        assert 'data-screen="0"' in dashboard.text
        assert 'data-screen="4"' in dashboard.text
        assert f'data-default-category="{CATEGORY_LOVE}"' in dashboard.text
        api_fields_attribute = re.search(
            r'data-api-fields="([^"]+)"', dashboard.text
        )
        assert api_fields_attribute is not None
        assert (
            json.loads(html.unescape(api_fields_attribute.group(1))) == API_FIELDS
        )

        frontend_script = client.get("/static/app.js")
        assert frontend_script.status_code == 200
        assert 'fetch("/auth/session-token"' in frontend_script.text
        assert '"/api/reading"' in frontend_script.text
        assert '"/api/reading/download"' in frontend_script.text

        token_response = client.post("/auth/session-token")
        assert token_response.status_code == 200
        access_token = token_response.json()[FIELD_ACCESS_TOKEN]
        headers = {"Authorization": f"Bearer {access_token}"}

        reading_response = client.post(
            "/api/reading",
            headers=headers,
            json={FIELD_CATEGORY: CATEGORY_LOVE, FIELD_QUESTION: SAMPLE_QUESTION},
        )
        assert reading_response.status_code == 200
        reading = reading_response.json()
        assert reading[FIELD_QUESTION] == SAMPLE_QUESTION
        assert len(reading[FIELD_CARDS]) == 3

        download_response = client.post(
            "/api/reading/download",
            headers=headers,
            json={
                FIELD_CATEGORY: reading[FIELD_CATEGORY],
                FIELD_CARDS: [
                    {
                        FIELD_POSITION: card[FIELD_POSITION],
                        FIELD_NAME: card[FIELD_NAME],
                    }
                    for card in reading[FIELD_CARDS]
                ],
            },
        )
        assert download_response.status_code == 200
        with ZipFile(BytesIO(download_response.content)) as archive:
            assert len(archive.namelist()) == 3
            assert all(
                archive.read(name).startswith(b"<svg ")
                for name in archive.namelist()
            )

        logout_response = client.post("/auth/logout", follow_redirects=False)
        assert logout_response.status_code == 303
        assert client.get("/", follow_redirects=False).headers["location"] == "/login"
