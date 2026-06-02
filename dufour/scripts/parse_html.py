import json
import os
from bs4 import BeautifulSoup
from backend.database import get_session, create_all
from backend.models import Topic, BibleReference


def parse_html(html_content: str) -> list[dict]:
    """Parst HTML-Inhalt und extrahiert Thema, Bibelstellen und Kategorien."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Thema aus der <h1> Überschrift extrahieren
    topic = soup.h1.get_text(strip=True) if soup.h1 else ""
    results = []

    # Alle <p> Absätze durchgehen
    for p in soup.find_all("p"):
        # Alle Links (<a href="...">) in diesem Absatz finden
        for a in p.find_all("a", href=True):
            reference = a.get_text(strip=True)  # Link-Text als Referenz (z.B. "Wasser")
            if not reference:
                continue
            # Kategorie anhand des Absatz-Textes bestimmen
            category = _determine_category(p, reference)
            results.append({
                "topic": topic,
                "reference": reference,
                "category": category,
            })

    return results


def _determine_category(paragraph, reference: str) -> str:
    """Bestimmt die Kategorie einer Bibelstelle anhand der enthaltenen Buch-Abkürzungen."""
    text = paragraph.get_text()
    
    # Prüfen auf Evangelien (Matthäus, Markus, Lukas, Johannes)
    if any(term in text for term in ["Mt ", "Mk ", "Lk ", "Joh "]):
        return "Evangelien"
    
    # Prüfen auf restliches Neues Testament (Briefe, Offenbarung)
    if any(term in text for term in ["Röm ", "1 Kor ", "2 Kor ", "Gal ", "Eph ", "Phil ", "Kol ",
                                       "1 Thess ", "2 Thess ", "1 Tim ", "2 Tim ", "Tit ", "Phlm ",
                                       "Hebr ", "Jak ", "1 Petr ", "2 Petr ", "1 Joh ", "2 Joh ",
                                       "3 Joh ", "Jud ", "Offb "]):
        return "Neues Testament"
    
    # Prüfen auf Propheten (Jesaja, Jeremia, Ezechiel, Daniel, kleine Propheten)
    if any(term in text for term in ["Jes ", "Jer ", "Ez ", "Dan ", "Hos ", "Joel ", "Am ", "Obd ",
                                       "Jon ", "Mi ", "Nah ", "Hab ", "Zef ", "Hag ", "Sach ", "Mal "]):
        return "Propheten"
    
    # Alles andere fällt unter Altes Testament (Genesis, Exodus, Psalmen, Sprüche, etc.)
    return "Altes Testament"


def save_to_db(data: list[dict]) -> None:
    """Speichert geparste Daten in der SQLite-Datenbank."""
    create_all()  # Tabellen erstellen falls nicht vorhanden
    session = next(get_session())  # DB-Sitzung öffnen
    try:
        for entry in data:
            # Prüfen ob Topic bereits existiert (Duplikate vermeiden)
            topic = session.query(Topic).filter_by(name=entry["topic"]).first()
            if not topic:
                topic = Topic(name=entry["topic"])
                session.add(topic)
                session.flush()  # topic.id wird erst nach flush vergeben

            # Neue Bibelreferenz erstellen und mit Topic verknüpfen
            ref = BibleReference(
                reference=entry["reference"],
                category=entry["category"],
                topic_id=topic.id
            )
            session.add(ref)
        session.commit()  # Alle Änderungen in DB schreiben
    except Exception:
        session.rollback()  # Bei Fehler alle Änderungen rückgängig machen
        raise
    finally:
        session.close()  # Sitzung immer schließen


if __name__ == "__main__":
    # Hauptprogramm: Liest alle HTML-Dateien aus data/, parst sie und speichert in DB
    data_dir = "data"
    all_results = []
    
    # Alle HTML-Dateien im data/ Ordner einlesen
    for filename in os.listdir(data_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(data_dir, filename)
            # Encoding versuchen: UTF-8, falls fehlschlag Latin-1
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    html = f.read()
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="latin-1") as f:
                    html = f.read()
            all_results.extend(parse_html(html))
    
    # Ergebnisse in Datenbank speichern
    if all_results:
        save_to_db(all_results)
        print(f"Saved {len(all_results)} references to database.")
    else:
        print("No data to save.")