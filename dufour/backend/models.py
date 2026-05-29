from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    references = relationship("BibleReference", back_populates="topic", cascade="all, delete-orphan")


class BibleReference(Base):
    __tablename__ = "bible_references"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, nullable=False)
    category = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    topic = relationship("Topic", back_populates="references")