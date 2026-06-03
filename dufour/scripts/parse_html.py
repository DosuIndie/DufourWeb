import os
import re
from bs4 import BeautifulSoup
from backend.database import get_session, create_all
from backend.models import Topic, BibleReference


# Katalog anerkannter deutscher Bibelstellen-Abkürzungen.
# Mehrwortige (z.B. "1 Petr") werden zuerst gematcht.
BIBLE_BOOKS = [
    # Mehrwortige Abkürzungen (längste zuerst)
    "1 Sam", "2 Sam", "1 Kön", "2 Kön", "1 Chr", "2 Chr", "1 Makk", "2 Makk",
    "1 Kor", "2 Kor", "1 Thess", "2 Thess", "1 Tim", "2 Tim",
    "1 Petr", "2 Petr", "1 Joh", "2 Joh", "3 Joh",
    "1 Pt", "2 Pt",
    # Einwortige Abkürzungen
    "Gen", "Gn", "Ex", "Lev", "Num", "Dtn", "Dt", "Jos", "Ri", "Idc",
    "Rut", "Rt", "Esr", "Neh", "Tob", "Jdt", "Est",
    "Ijob", "Jb", "Hi", "Ps", "Pss", "Spr", "Koh", "Eccl", "Hld",
    "Weish", "Wis", "Sir",
    "Jes", "Is", "Jer", "Jr", "Klgl", "Lam", "Bar", "Ez", "Ezech",
    "Dan", "Dn", "Hos", "Os", "Joel", "Am", "Obd", "Ob", "Jon",
    "Mi", "Nah", "Hab", "Zef", "Hag", "Sach", "Mal",
    "Mt", "Mat", "Mk", "Mc", "Lk", "Joh", "Apg", "Röm",
    "Gal", "Eph", "Phil", "Phl", "Kol", "Tit", "Phlm", "Phm",
    "Hebr", "Jak", "Jac", "Jud", "Offb", "Apk", "Off",
]
BIBLE_BOOKS = sorted(set(BIBLE_BOOKS), key=len, reverse=True)
BOOK_PATTERN = "|".join(re.escape(b) for b in BIBLE_BOOKS)

# Vollständige Referenz: <Buch> <Kapitel>,<Vers> [f|ff] [-<Vers>] [. <Vers>]* [par.]?
# Gruppe 1: Buch, Gruppe 2: Kapitel, Gruppe 3: Vers
BIBLE_REF_RE = re.compile(
    r"\b(" + BOOK_PATTERN + r")"
    r"\s+\d+"
    r"\s*[,\.]\s*\d+"
    r"(?:\s*[a-zäöüß]{1,2})?"
    r"(?:\s*-\s*\d+(?:\s*[a-zäöüß]{1,2})?)?"
    r"(?:\s*\.\s*\d+(?:\s*[a-zäöüß]{1,2})?)*"
    r"(?:\s+par\.)?",
    re.UNICODE,
)

# Kategorisierung der Bücher
EVANGELIEN = {"Mt", "Mat", "Mk", "Mc", "Lk", "Joh"}
NT = EVANGELIEN | {
    "Apg", "Röm", "1 Kor", "2 Kor", "Gal", "Eph", "Phil", "Phl", "Kol",
    "1 Thess", "2 Thess", "1 Tim", "2 Tim", "Tit", "Phlm", "Phm",
    "Hebr", "Jak", "Jac", "1 Petr", "2 Petr", "1 Pt", "2 Pt",
    "1 Joh", "2 Joh", "3 Joh", "Jud", "Offb", "Apk", "Off",
}
PROPHETEN = {
    "Jes", "Is", "Jer", "Jr", "Klgl", "Lam", "Bar", "Ez", "Ezech",
    "Dan", "Dn", "Hos", "Os", "Joel", "Am", "Obd", "Ob", "Jon",
    "Mi", "Nah", "Hab", "Zef", "Hag", "Sach", "Mal",
}


def _classify(book: str) -> str:
    """Ordnet eine Buch-Abkürzung einer der vier Kategorien zu."""
    if book in EVANGELIEN:
        return "Evangelien"
    if book in NT:
        return "Neues Testament"
    if book in PROPHETEN:
        return "Propheten"
    return "Altes Testament"


def _normalize_reference(text: str) -> str:
    """Bereinigt eine extrahierte Referenz (überflüssige Leerzeichen, Trailing 'par.')."""
    text = re.sub(r"\s+par\.\s*$", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_html(html_content: str) -> list[dict]:
    """Parst HTML-Inhalt und extrahiert Thema + Bibelstellen mit Kategorie."""
    soup = BeautifulSoup(html_content, "html.parser")
    topic = soup.h1.get_text(strip=True) if soup.h1 else ""
    if not topic:
        return []

    results: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        for match in BIBLE_REF_RE.finditer(text):
            book = match.group(1)
            ref = _normalize_reference(match.group(0))
            if not ref:
                continue
            category = _classify(book)
            key = (ref, category)
            if key in seen:
                continue
            seen.add(key)
            results.append({"topic": topic, "reference": ref, "category": category})

    return results


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