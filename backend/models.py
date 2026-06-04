from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Topic(Base):
    """Modell für ein Thema (z.B. "Glaube", "BAUM"). Ein Thema kann viele Bibelstellen haben."""
    __tablename__ = "topics"  # Name der Datenbanktabelle

    id = Column(Integer, primary_key=True, index=True)  # Eindeutige ID (Primärschlüssel)
    name = Column(String, unique=True, nullable=False)  # Themenname (z.B. "Glaube"), darf nicht doppelt vorkommen

    # Beziehung zu BibleReference: Ein Topic hat viele Bibelstellen
    # cascade="all, delete-orphan": Wird ein Topic gelöscht, werden alle zugehörigen Referenzen mitgelöscht
    references = relationship("BibleReference", back_populates="topic", cascade="all, delete-orphan")


class BibleReference(Base):
    """Modell für eine einzelne Bibelstelle (z.B. "Hebr 11,1" mit Kategorie "Neues Testament")."""
    __tablename__ = "bible_references"  # Name der Datenbanktabelle

    id = Column(Integer, primary_key=True, index=True)  # Eindeutige ID
    reference = Column(String, nullable=False)  # Bibelstellenangabe (z.B. "Gen 1,1")
    category = Column(String, nullable=False)  # Kategorie (z.B. "Altes Testament", "Evangelien")
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)  # Verweis auf das zugehörige Topic

    # Beziehung zu Topic: Diese Bibelstelle gehört zu genau einem Thema
    topic = relationship("Topic", back_populates="references")