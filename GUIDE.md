# Dufour – Development Guide

Dieses Dokument beschreibt alle Entwicklungsaufgaben als klare Tasks für den KI-Assistenten.
**Immer nur eine Task auf einmal an das Modell geben.**

---

## Aktueller Status

- [ ] Commit 1 – Projektstruktur
- [ ] Commit 2 – Parser: HTML → JSON
- [ ] Commit 3 – Parser: JSON → SQLite
- [ ] Commit 4 – DB Modelle
- [ ] Commit 5 – Such-Endpoint
- [ ] Commit 6 – Passwort-Auth
- [ ] Commit 7 – Auth-Middleware
- [ ] Commit 8 – Frontend: Login
- [ ] Commit 9 – Frontend: Suche
- [ ] Commit 10 – Refactor & Cleanup

Nach jedem abgeschlossenen Commit: `[x]` setzen.

---

## ✅ Health-Check – Implementierungsstand prüfen

Diese Task zuerst ausführen wenn du das Modell gewechselt hast
oder dir unsicher bist ob alles korrekt implementiert wurde.

### Aider-Befehl
```
/add backend/database.py backend/models.py backend/main.py
/add backend/routers/auth.py backend/routers/search.py
/add scripts/parse_html.py tests/test_parser.py
Read all added files carefully.
Do NOT change any code.
For each file report:
1. Is the file empty or just `pass`? → Status: MISSING
2. Does it have real implementation? → Status: DONE
3. Are there obvious import errors or missing dependencies? → Status: BROKEN
Output a simple table:
File | Status | Issue (if any)
```

### Akzeptanzkriterium
Alle Dateien zeigen DONE und keine BROKEN-Einträge.

### Manuell prüfen
```bash
# Alle Tests laufen lassen
pytest -v

# Imports testen
python -c "from backend.database import get_session; print('DB OK')"
python -c "from backend.models import Topic, BibleReference; print('Models OK')"
python -c "from scripts.parse_html import parse_html, save_to_db; print('Parser OK')"
```

---

## Task: Commit 1 – Projektstruktur

### Ziel
Projektstruktur und `requirements.txt` anlegen.

### Regeln
- Nur Ordner und leere Dateien erstellen
- Keine Implementierung
- Max 20 lines in requirements.txt

### Dateien anlegen
```
dufour/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── routers/
│       ├── __init__.py
│       ├── search.py
│       └── auth.py
├── frontend/
│   ├── login.html
│   └── search.html
├── data/
│   └── .gitignore      ← Inhalt: *
├── scripts/
│   ├── __init__.py
│   └── parse_html.py
├── tests/
│   └── __init__.py
├── .env                ← Inhalt: APP_PASSWORD=secret
├── .gitignore
└── requirements.txt
```

### requirements.txt Inhalt
```
fastapi
uvicorn
sqlalchemy
beautifulsoup4
python-dotenv
pytest
httpx
```

### .gitignore Inhalt
```
data/
.env
*.db
.venv/
__pycache__/
.aider*
```

### Akzeptanzkriterium
```bash
pip install -r requirements.txt  # kein Fehler
```

### Commit
```
build: initial project structure and requirements
```

---

## Task: Commit 2 – Parser: HTML → JSON

### Ziel
`scripts/parse_html.py` liest HTML-Dateien und gibt geparste Daten als JSON aus.
Noch keine Datenbankanbindung.

### Regeln
- Nur `scripts/parse_html.py` und `tests/test_parser.py` bearbeiten
- Max 30 lines pro Datei
- Kein DB-Import in diesem Commit

### Aider-Befehl
```
/add scripts/parse_html.py tests/test_parser.py
```

### parse_html.py soll enthalten
- Funktion `parse_html(html_content: str) -> list[dict]`
- Nutzt BeautifulSoup4
- Extrahiert pro Eintrag: `topic`, `reference`, `category`
- `category` ist eines von:
  `Altes Testament`, `Propheten`, `Neues Testament`, `Evangelien`
- Gibt Liste von Dicts zurück
- `if __name__ == "__main__":` Block liest aus `data/` und printet JSON

### test_parser.py soll enthalten
- Inline-HTML-String als Testdaten (kein echtes File)
- Test: `parse_html()` gibt mindestens einen Eintrag zurück
- Test: topic, reference, category sind nicht leer

### Akzeptanzkriterium
```bash
pytest tests/test_parser.py -v   # PASSED
python scripts/parse_html.py     # JSON-Output in Terminal
```

### Commit
```
feat(parser): extract topics and bible references from HTML to JSON
```

---

## Task: Commit 4 – DB Modelle

### Achtung
Commit 4 vor Commit 3 ausführen, da Commit 3 die Modelle importiert.

### Ziel
`backend/database.py` und `backend/models.py` implementieren.

### Regeln
- Max 25 lines pro Datei
- Keine Business-Logik in models.py
- `get_session()` muss exportiert werden

### Aider-Befehl
```
/add backend/database.py backend/models.py
```

### database.py soll enthalten
```python
# ENGINE via DATABASE_URL aus .env (python-dotenv)
# Base = declarative_base()
# SessionLocal
# get_session() -> Session
# create_all() Aufruf
```

### models.py soll enthalten
```python
# Topic: id (PK int), name (str, unique)
# BibleReference: id (PK int), reference (str),
#   category (str), topic_id (FK → Topic.id)
```

### Akzeptanzkriterium
```bash
python -c "from backend.database import get_session; print('OK')"
python -c "from backend.models import Topic, BibleReference; print('OK')"
pytest tests/test_models.py -v   # PASSED
```

### Commit
```
feat(db): add Topic and BibleReference models
```

---

## Task: Commit 3 – Parser: JSON → SQLite

### Voraussetzung
Commit 4 (DB Modelle) muss abgeschlossen sein.

### Ziel
`save_to_db()` Funktion in `scripts/parse_html.py` ergänzen.
Geparste Daten werden in SQLite gespeichert.

### Regeln
- Nur `scripts/parse_html.py` und `tests/test_parser.py` bearbeiten
- Max 25 lines neue Code
- Duplikate überspringen (Topic bereits vorhanden → kein Fehler)

### Aider-Befehl
```
/add scripts/parse_html.py tests/test_parser.py
/add backend/database.py backend/models.py
```

### parse_html.py soll zusätzlich enthalten
```python
# save_to_db(data: list[dict]) -> None
# Importiert: get_session, Topic, BibleReference
# Topic-Duplikat-Check vor Insert
# session.flush() vor BibleReference-Insert
# Fehlerbehandlung mit rollback
```

### test_parser.py soll zusätzlich enthalten
- Test: `save_to_db()` aufrufen mit Sample-Daten
- DB abfragen: mindestens ein `BibleReference` Eintrag vorhanden

### Akzeptanzkriterium
```bash
pytest tests/test_parser.py -v   # PASSED
python scripts/parse_html.py     # DB wird befüllt
sqlite3 dufour.db "SELECT * FROM bible_references LIMIT 5;"
```

### Commit
```
feat(parser): persist parsed JSON data to SQLite
```

---

## Task: Commit 5 – Such-Endpoint

### Voraussetzung
Commit 3 und 4 müssen abgeschlossen sein.

### Ziel
`GET /search?q=<string>` Endpoint in `backend/routers/search.py`.

### Regeln
- Nur `backend/routers/search.py` und `tests/test_search.py` bearbeiten
- Max 40 lines
- Noch kein Auth-Check in diesem Commit

### Aider-Befehl
```
/add backend/routers/search.py tests/test_search.py
/add backend/database.py backend/models.py backend/main.py
```

### search.py soll enthalten
```python
# GET /search?q=
# Case-insensitiver Partial-Match auf Topic.name
# Rückgabe:
# {
#   "topic": "...",
#   "results": {
#     "Altes Testament": [],
#     "Propheten": [],
#     "Neues Testament": [],
#     "Evangelien": []
#   }
# }
```

### test_search.py soll enthalten
- FastAPI TestClient
- Test: Suche nach bekanntem Topic → Ergebnis nicht leer
- Test: Suche nach unbekanntem Topic → leere results

### Akzeptanzkriterium
```bash
pytest tests/test_search.py -v
uvicorn backend.main:app --reload
curl "http://localhost:8000/search?q=Glaube"
```

### Commit
```
feat(search): add GET /search?q= endpoint
```

---

## Task: Commit 6 – Passwort-Auth

### Ziel
`POST /login` Endpoint in `backend/routers/auth.py`.

### Regeln
- Nur `backend/routers/auth.py` und `tests/test_auth.py` bearbeiten
- Max 30 lines
- Passwort aus `.env` via `python-dotenv`
- Bei Erfolg: httponly Cookie `session=authenticated` setzen

### Aider-Befehl
```
/add backend/routers/auth.py tests/test_auth.py backend/main.py
```

### auth.py soll enthalten
```python
# POST /login
# Body: {"password": "..."}
# Vergleich mit APP_PASSWORD aus .env
# Erfolg (200): Cookie session=authenticated setzen (httponly)
# Fehler (401): {"detail": "Falsches Passwort"}
```

### test_auth.py soll enthalten
- Test: richtiges Passwort → 200 + Cookie gesetzt
- Test: falsches Passwort → 401

### Akzeptanzkriterium
```bash
pytest tests/test_auth.py -v
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"password": "secret"}'
```

### Commit
```
feat(auth): add POST /login with simple password check
```

---

## Task: Commit 7 – Auth-Middleware

### Voraussetzung
Commit 6 muss abgeschlossen sein.

### Ziel
`GET /search` mit Session-Cookie schützen.

### Regeln
- Nur `backend/main.py` und `tests/test_auth.py` bearbeiten
- Max 20 lines neue Code

### Aider-Befehl
```
/add backend/main.py tests/test_auth.py backend/routers/search.py
```

### main.py soll enthalten
```python
# Dependency-Funktion require_auth(request: Request)
# Prüft: cookie "session" == "authenticated"
# Falls nicht: HTTPException 401
# Dependency auf GET /search anwenden
```

### test_auth.py soll zusätzlich enthalten
- Test: `/search` ohne Cookie → 401
- Test: `/search` mit Cookie → 200

### Akzeptanzkriterium
```bash
pytest tests/test_auth.py -v
# Ohne Cookie:
curl http://localhost:8000/search?q=Glaube        # → 401
# Mit Cookie:
curl -b "session=authenticated" \
  http://localhost:8000/search?q=Glaube           # → 200
```

### Commit
```
feat(auth): protect /search route with session cookie middleware
```

---

## Task: Commit 8 – Frontend: Login

### Ziel
`frontend/login.html` – einfache Login-Seite.

### Regeln
- Nur `frontend/login.html` bearbeiten
- Kein CSS-Framework
- Max 50 lines

### Aider-Befehl
```
/add frontend/login.html
```

### login.html soll enthalten
- Passwort-Input + Submit-Button
- `POST /login` mit `fetch()` aufrufen
- Erfolg (200): weiterleiten zu `search.html`
- Fehler (401): Text "Falsches Passwort" anzeigen
- Minimales, lesbares CSS inline

### Akzeptanzkriterium
```
Browser: http://localhost:8000/login.html
→ Falsches Passwort eingeben → Fehlermeldung
→ Richtiges Passwort eingeben → Weiterleitung zu search.html
```

### Commit
```
feat(frontend): add login page
```

---

## Task: Commit 9 – Frontend: Suche

### Voraussetzung
Commit 8 muss abgeschlossen sein.

### Ziel
`frontend/search.html` – Suchmaske mit kategorisierten Ergebnissen.

### Regeln
- Nur `frontend/search.html` bearbeiten
- Kein CSS-Framework
- Max 50 lines

### Aider-Befehl
```
/add frontend/search.html
```

### search.html soll enthalten
- Text-Input für Thema + Submit-Button
- `GET /search?q=...` mit `fetch()` aufrufen (Cookie wird automatisch mitgeschickt)
- Ergebnisse in 4 Sektionen anzeigen:
  `Altes Testament | Propheten | Neues Testament | Evangelien`
- Bei 401: weiterleiten zu `login.html`
- Leere Kategorien ausblenden oder als "–" anzeigen

### Akzeptanzkriterium
```
Browser: http://localhost:8000/search.html
→ Thema eingeben → Ergebnisse erscheinen in 4 Kategorien
→ Session abgelaufen → Weiterleitung zu login.html
```

### Commit
```
feat(frontend): add search page with categorized results
```

---

## Task: Commit 10 – Refactor & Cleanup

### Ziel
Code aufräumen ohne neue Features.

### Regeln
- Keine neuen Features
- Max 50 lines geändert gesamt
- Alle Tests müssen danach noch grün sein

### Aider-Befehl
```
/add backend/database.py backend/models.py backend/main.py
/add backend/routers/auth.py backend/routers/search.py
/add scripts/parse_html.py
```

### Aufgaben
```
1. Docstrings zu allen Funktionen hinzufügen
2. Ungenutzte Imports entfernen
3. Type Hints prüfen und ergänzen
4. Sicherstellen: keine Datei über 80 lines
5. pytest läuft ohne Fehler durch
```

### Akzeptanzkriterium
```bash
pytest -v                     # alle PASSED
python -m ruff check .        # keine Fehler
python -m black --check .     # keine Fehler
```

### Commit
```
refactor: cleanup, docstrings and line limit check
```

---

## 🔧 Nützliche Befehle

```bash
# Server starten
uvicorn backend.main:app --reload

# Alle Tests
pytest -v

# Einzelne Test-Datei
pytest tests/test_parser.py -v

# DB zurücksetzen
rm dufour.db && python scripts/parse_html.py

# DB direkt inspizieren
sqlite3 dufour.db
> .tables
> SELECT * FROM topics;
> SELECT * FROM bible_references LIMIT 10;
> .quit

# Aider starten (empfohlen)
aider --model ollama/qwen3:27b --no-auto-commits
```
