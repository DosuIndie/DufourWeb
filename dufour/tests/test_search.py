import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import get_session, create_all, SessionLocal
from backend.models import Topic, BibleReference


def _insert_test_data():
    """Hilfsfunktion: Testdaten in die DB einfügen."""
    session = SessionLocal()
    try:
        topic = Topic(name="Glaube")
        session.add(topic)
        session.commit()

        refs = [
            BibleReference(reference="Hebr 11,1", category="Neues Testament", topic_id=topic.id),
            BibleReference(reference="Röm 1,17", category="Neues Testament", topic_id=topic.id),
            BibleReference(reference="Gen 15,6", category="Altes Testament", topic_id=topic.id),
        ]
        session.add_all(refs)
        session.commit()
    finally:
        session.close()


@pytest.fixture
def client():
    """Create a test client with clean database."""
    # Tabellen erstellen (erst dann existieren sie)
    create_all()
    
    # Testdaten einfügen
    _insert_test_data()
    
    with TestClient(app) as c:
        yield c
    
    # Datenbank aufräumen nach dem Test
    session = SessionLocal()
    session.query(BibleReference).delete()
    session.query(Topic).delete()
    session.commit()
    session.close()


def test_search_existing_topic(client):
    """Test: Search for an existing topic returns results."""
    response = client.get("/search?q=Glaube")
    assert response.status_code == 200
    data = response.json()
    
    assert data["topic"] == "Glaube"
    assert len(data["results"]["Neues Testament"]) == 2
    assert len(data["results"]["Altes Testament"]) == 1
    assert len(data["results"]["Propheten"]) == 0
    assert len(data["results"]["Evangelien"]) == 0


def test_search_nonexistent_topic(client):
    """Test: Search for a non-existing topic returns empty results."""
    response = client.get("/search?q=ExistiertNicht")
    assert response.status_code == 200
    data = response.json()
    
    assert data["topic"] == "ExistiertNicht"
    assert all(len(v) == 0 for v in data["results"].values())


def test_search_case_insensitive(client):
    """Test: Search is case-insensitive."""
    response = client.get("/search?q=glaube")
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Glaube"


def test_search_partial_match(client):
    """Test: Partial match works (search for 'Glau')."""
    response = client.get("/search?q=Glau")
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Glaube"