from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from backend.database import get_session
from backend.models import Topic, BibleReference

router = APIRouter()


@router.get("/search")
def search_topics(q: str = Query(..., min_length=1)):
    """Search for topics by name (case-insensitive partial match)."""
    session = next(get_session())
    try:
        topic = session.query(Topic).filter(Topic.name.ilike(f"%{q}%")).first()

        if not topic:
            return {
                "topic": q,
                "results": {
                    "Altes Testament": [],
                    "Propheten": [],
                    "Neues Testament": [],
                    "Evangelien": []
                }
            }

        references = session.query(BibleReference).filter(BibleReference.topic_id == topic.id).all()

        results = {
            "Altes Testament": [],
            "Propheten": [],
            "Neues Testament": [],
            "Evangelien": []
        }
        for ref in references:
            results[ref.category].append(ref.reference)

        return {
            "topic": topic.name,
            "results": results
        }
    finally:
        session.close()