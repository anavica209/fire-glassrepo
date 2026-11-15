import pytest

from app.core.config import _database_url


def test_database_url_is_required_instead_of_component_fallback(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_DB_HOST", "db.example.test")
    monkeypatch.setenv("POSTGRES_DB_PASS", "test-password")

    with pytest.raises(ValueError, match="DATABASE_URL"):
        _database_url()


def test_database_url_uses_pooler_url_and_password_env(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres.project-ref@pooler.example.test:5432/postgres"
        "?sslmode=require",
    )
    monkeypatch.setenv("POSTGRES_DB_PASS", "test-password")

    url = _database_url()

    assert url.drivername == "postgresql+asyncpg"
    assert url.host == "pooler.example.test"
    assert url.username == "postgres.project-ref"
    assert url.password == "test-password"
    assert url.query == {"ssl": "require"}
