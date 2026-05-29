import json
import os
from bs4 import BeautifulSoup
from backend.database import get_session, create_all
from backend.models import Topic, BibleReference


def parse_html(html_content: str) -> list[dict]:
    """Parse HTML content and extract topic, references with categories."""
    soup = BeautifulSoup(html_content, "html.parser")
    topic = soup.h1.get_text(strip=True) if soup.h1 else ""
    results = []

    for p in soup.find_all("p"):
        for a in p.find_all("a", href=True):
            reference = a.get_text(strip=True)
            if not reference:
                continue
            category = _determine_category(p, reference)
            results.append({
                "topic": topic,
                "reference": reference,
                "category": category,
            })

    return results


def _determine_category(paragraph, reference: str) -> str:
    """Heuristic category detection based on paragraph content."""
    text = paragraph.get_text()
    
    if any(term in text for term in ["Mt ", "Mk ", "Lk ", "Joh "]):
        return "Evangelien"
    if any(term in text for term in ["Röm ", "1 Kor ", "2 Kor ", "Gal ", "Eph ", "Phil ", "Kol ",
                                       "1 Thess ", "2 Thess ", "1 Tim ", "2 Tim ", "Tit ", "Phlm ",
                                       "Hebr ", "Jak ", "1 Petr ", "2 Petr ", "1 Joh ", "2 Joh ",
                                       "3 Joh ", "Jud ", "Offb "]):
        return "Neues Testament"
    if any(term in text for term in ["Jes ", "Jer ", "Ez ", "Dan ", "Hos ", "Joel ", "Am ", "Obd ",
                                       "Jon ", "Mi ", "Nah ", "Hab ", "Zef ", "Hag ", "Sach ", "Mal "]):
        return "Propheten"
    return "Altes Testament"


def save_to_db(data: list[dict]) -> None:
    """Save parsed data to SQLite database."""
    create_all()
    session = next(get_session())
    try:
        for entry in data:
            # Check if topic already exists
            topic = session.query(Topic).filter_by(name=entry["topic"]).first()
            if not topic:
                topic = Topic(name=entry["topic"])
                session.add(topic)
                session.flush()

            ref = BibleReference(
                reference=entry["reference"],
                category=entry["category"],
                topic_id=topic.id
            )
            session.add(ref)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    data_dir = "data"
    all_results = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    html = f.read()
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="latin-1") as f:
                    html = f.read()
            all_results.extend(parse_html(html))
    
    if all_results:
        save_to_db(all_results)
        print(f"Saved {len(all_results)} references to database.")
    else:
        print("No data to save.")