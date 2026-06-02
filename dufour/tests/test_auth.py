import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Erstellt einen Test-Client ohne Datenbank-Initialisierung."""
    with TestClient(app) as c:
        yield c


def test_login_success(client):
    """Test: Richtiges Passwort → 200 + Cookie gesetzt."""
    response = client.post("/login", json={"password": "secret"})
    assert response.status_code == 200
    assert response.cookies.get("session") == "authenticated"


def test_login_wrong_password(client):
    """Test: Falsches Passwort → 401."""
    response = client.post("/login", json={"password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Falsches Passwort"


def test_search_without_cookie_returns_401(client):
    """Test: /search ohne Session-Cookie → 401."""
    response = client.get("/search?q=Glaube")
    assert response.status_code == 401


def test_search_with_cookie_returns_200(client, monkeypatch):
    """Test: /search mit gültigem Session-Cookie → 200."""
    # Wir müssen eine gültige Session haben
    # Zuerst einloggen, um den Cookie zu bekommen
    login_response = client.post("/login", json={"password": "secret"})
    assert login_response.status_code == 200

    # Cookie aus dem Login-Response holen
    cookie = login_response.cookies.get("session")
    
    # Jetzt mit dem Cookie die Suche aufrufen
    response = client.get("/search?q=Glaube", cookies={"session": cookie})
    assert response.status_code == 200
