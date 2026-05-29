import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Topic, BibleReference
from scripts.parse_html import parse_html, save_to_db


@pytest.fixture
def db_session():
    """Create a fresh in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def test_parse_html_returns_list():
    html = """
    <html><head></head><body>
    <h1>Glaube</h1>
    <p>Der Glaube ist ein Fundament (vgl. <a href="HEBR.html">Hebr 11,1</a>).</p>
    </body></html>
    """
    results = parse_html(html)
    assert isinstance(results, list)
    assert len(results) > 0


def test_parse_html_fields_not_empty():
    html = """
    <html><head></head><body>
    <h1>BAUM</h1>
    <p>Der Gerechte ist wie ein Baum (Ps 1,3).</p>
    <p>Jesus sagte: Ich bin der Weinstock (<a href="JOH.html">Joh 15,1</a>).</p>
    </body></html>
    """
    results = parse_html(html)
    for entry in results:
        assert entry["topic"] == "BAUM"
        assert entry["reference"] != ""
        assert entry["category"] != ""


def test_parse_html_empty_html():
    """Test with minimal HTML content."""
    html = "<html><head></head><body></body></html>"
    results = parse_html(html)
    assert results == []


def test_save_to_db_creates_bible_reference(monkeypatch, db_session):
    """Test that save_to_db creates BibleReference entries."""
    # Monkey-patch get_session to use our test session
    def mock_get_session():
        yield db_session

    monkeypatch.setattr("scripts.parse_html.get_session", mock_get_session)
    monkeypatch.setattr("scripts.parse_html.create_all", lambda: None)

    data = [
        {"topic": "Glaube", "reference": "Hebr 11,1", "category": "Neues Testament"},
        {"topic": "Glaube", "reference": "Röm 1,17", "category": "Neues Testament"},
    ]

    save_to_db(data)

    references = db_session.query(BibleReference).all()
    assert len(references) == 2
    assert references[0].reference == "Hebr 11,1"


def test_save_to_db_skips_duplicate_topic(monkeypatch, db_session):
    """Test that duplicate topics are handled gracefully."""
    def mock_get_session():
        yield db_session

    monkeypatch.setattr("scripts.parse_html.get_session", mock_get_session)
    monkeypatch.setattr("scripts.parse_html.create_all", lambda: None)

    # First save
    save_to_db([{"topic": "Glaube", "reference": "Hebr 11,1", "category": "Neues Testament"}])
    # Second save with same topic
    save_to_db([{"topic": "Glaube", "reference": "Röm 1,17", "category": "Neues Testament"}])

    topics = db_session.query(Topic).all()
    assert len(topics) == 1  # Only one topic entry