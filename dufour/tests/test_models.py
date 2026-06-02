import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Topic, BibleReference


@pytest.fixture
def db_session():
    """Erstellt eine frische In-Memory-Datenbank für jeden Test."""
    # In-Memory SQLite (keine Datei, schneller und isoliert)
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)  # Tabellen anlegen
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session  # Gibt Sitzung an den Test weiter
    session.close()  # Sitzung nach Test schließen


def test_create_topic(db_session):
    """Test: Ein Topic kann angelegt und aus der DB gelesen werden."""
    topic = Topic(name="Glaube")
    db_session.add(topic)
    db_session.commit()

    saved = db_session.query(Topic).filter_by(name="Glaube").first()
    assert saved is not None
    assert saved.name == "Glaube"


def test_create_bible_reference(db_session):
    """Test: Eine Bibelstelle kann mit einem Topic verknüpft angelegt werden."""
    topic = Topic(name="Glaube")
    db_session.add(topic)
    db_session.commit()

    ref = BibleReference(reference="Hebr 11,1", category="Neues Testament", topic_id=topic.id)
    db_session.add(ref)
    db_session.commit()

    saved = db_session.query(BibleReference).first()
    assert saved is not None
    assert saved.reference == "Hebr 11,1"
    assert saved.category == "Neues Testament"
    assert saved.topic_id == topic.id


def test_topic_references_relationship(db_session):
    """Test: Die 1-zu-n Beziehung zwischen Topic und BibleReference funktioniert."""
    topic = Topic(name="BAUM")
    db_session.add(topic)
    db_session.commit()

    ref1 = BibleReference(reference="Ps 1,3", category="Altes Testament", topic_id=topic.id)
    ref2 = BibleReference(reference="Mt 7,17", category="Evangelien", topic_id=topic.id)
    db_session.add_all([ref1, ref2])
    db_session.commit()

    assert len(topic.references) == 2  # Topic hat 2 Referenzen
    assert topic.references[0].reference in ["Ps 1,3", "Mt 7,17"]


def test_topic_unique_constraint(db_session):
    """Test: Doppelte Topic-Namen werden von der Datenbank abgelehnt."""
    topic1 = Topic(name="Glaube")
    db_session.add(topic1)
    db_session.commit()

    topic2 = Topic(name="Glaube")
    db_session.add(topic2)
    with pytest.raises(Exception):  # Erwartet: Datenbank-Fehler (IntegrityError)
        db_session.commit()