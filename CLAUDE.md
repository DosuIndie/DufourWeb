# CLAUDE.md

Dieses Dokument beschreibt die Standards, Struktur und Best Practices für die Entwicklung der **Dufour Bible Topic Search Application**. Es dient als Referenz für alle Commits und stellt sicher, dass jeder Entwicklungsschritt konsistent und wartbar bleibt.

---

# 🚀 Projektziel

Die Anwendung ermöglicht authentifizierten Nutzern eine schnelle themenbasierte Suche nach Bibelstellen.

HTML-Quelldateien werden geparst, Bibelstellen extrahiert und in einer SQLite-Datenbank gespeichert. Über ein einfaches Webinterface können Nutzer nach Themen suchen und Ergebnisse gegliedert nach theologischen Kategorien abrufen.

**Kernziele:**

- Themenbasierte Bibelstellensuche (Eingabe → Ergebnisse)
- Gliederung der Ergebnisse in vier Kategorien:
  - Altes Testament
  - Propheten
  - Neues Testament
  - Evangelien
- Einfaches Passwort-Login (kein User-Management)
- Saubere Datenpipeline aus HTML-Quelldateien
- Leichtgewichtiges Frontend ohne schwere Frameworks

---

# 📁 Projektstruktur

```text
dufour/
├── backend/
│   ├── main.py          # FastAPI App-Einstiegspunkt
│   ├── database.py      # SQLite + SQLAlchemy Setup
│   ├── models.py        # DB-Modelle
│   └── routers/
│       ├── search.py    # GET /search?q=
│       └── auth.py      # POST /login
├── frontend/
│   ├── login.html       # Passwort-Login
│   └── search.html      # Suchmaske + Ergebnisanzeige
├── data/                # HTML-Quelldateien (nicht im Git!)
├── scripts/
│   └── parse_html.py    # HTML-Parser → SQLite
├── tests/
├── .env                 # APP_PASSWORD=secret (nicht im Git!)
├── .gitignore
└── requirements.txt
```

---

# 🧩 Commit-Struktur

Jeder Commit folgt dem **Red → Green → Refactor** Prinzip und enthält maximal **50 Zeilen neuen Code**.

| Commit | Typ | Beschreibung |
|--------|-----|--------------|
| 1 | `build:` | initial project structure and requirements |
| 2 | `feat(parser):` | extract topics and bible references from HTML to JSON |
| 3 | `feat(parser):` | persist parsed JSON data to SQLite |
| 4 | `feat(db):` | add Topic and BibleReference models |
| 5 | `feat(search):` | add GET /search?q= endpoint |
| 6 | `feat(auth):` | add POST /login with simple password check |
| 7 | `feat(auth):` | protect /search route with session cookie middleware |
| 8 | `feat(frontend):` | add login page |
| 9 | `feat(frontend):` | add search page with categorized results |
| 10 | `refactor:` | cleanup, docstrings and line limit check |

---

# 🛠️ Entwicklungsstandards

## Code Style

- Python-Code muss **PEP 8** einhalten
- Formatierung mit `black`
- Imports sortieren mit `isort`
- Linting mit `ruff`

## Docstrings

Jede Funktion, Klasse und jedes Modul erhält einen Docstring:

```python
def search_topic(query: str) -> list[dict]:
    """
    Sucht Bibelstellen anhand eines Themas.

    :param query: Suchbegriff des Nutzers.
    :return: Liste von passenden Bibelstellen als Dictionaries.
    :raises ValueError: Falls query leer ist.
    """
```

## Type Hints

Alle Funktionen müssen explizite Type Hints verwenden:

```python
def parse_html_file(path: str) -> list[dict]:
```

---

# 🏗️ Architektur

## API-Schicht (`backend/routers/`)

- HTTP-Routing via FastAPI
- Request-Validierung
- Auth-Check (Session-Cookie)
- Response-Serialisierung

## Datenzugriffsschicht (`backend/models.py`, `backend/database.py`)

- SQLAlchemy ORM-Modelle
- Kein Business-Logic in dieser Schicht

## Frontend (`frontend/`)

- Vanilla HTML / CSS / JavaScript
- Kein schweres Framework
- Cookie-basierte Auth-Weiterleitung

---

# 💾 Datenbankstruktur

## topics

| Feld | Typ |
|------|-----|
| id | Integer PK |
| name | String (unique) |

## bible_references

| Feld | Typ |
|------|-----|
| id | Integer PK |
| reference | String (z.B. "Gen 1,1") |
| category | String (Enum: siehe Kategorien) |
| topic_id | FK → topics.id |

**Erlaubte Kategorien:**
- `Altes Testament`
- `Propheten`
- `Neues Testament`
- `Evangelien`

---

# 🔄 Datenpipeline (`scripts/parse_html.py`)

```
1. Ingestion   → HTML-Dateien aus data/ lesen (BeautifulSoup4)
2. Extraktion  → Thema + Bibelstelle + Kategorie extrahieren
3. Validierung → Kategorie prüfen, Duplikate überspringen, Fehler loggen
4. Persistenz  → Via SQLAlchemy in SQLite schreiben (nie direktes SQL)
```

---

# 🔐 Authentifizierung

- **Aktuell:** Einfaches Passwort aus `.env` (`APP_PASSWORD`)
- Login via `POST /login` mit `{"password": "..."}`
- Bei Erfolg: httponly Session-Cookie `session=authenticated`
- Geschützte Route: `GET /search` prüft Cookie

**Sicherheitsregeln:**
- `.env` niemals in Git committen
- Passwort niemals hardcoden
- Input immer validieren

---

# 🔍 Suchverhalten

- Eingabe: Thema als Freitext
- Matching: case-insensitiv, Partial-Match
- Ausgabe: Bibelstellen gruppiert nach 4 Kategorien

```json
{
  "topic": "Glaube",
  "results": {
    "Altes Testament": ["Gen 1,1"],
    "Propheten": [],
    "Neues Testament": ["Röm 3,28"],
    "Evangelien": ["Joh 3,16"]
  }
}
```

---

# 🧪 Teststrategie

- **Red → Green → Refactor** bei jedem Commit
- Jeder Commit beginnt mit einem **fehlschlagenden Test**
- Testframework: `pytest` + `httpx` (FastAPI TestClient)
- Ziel: 80 % Coverage für Backend-Logik und Parser

### Testarten

| Art | Beispiel |
|-----|----------|
| Unit | Parser mit inline HTML-String |
| Integration | Such-Endpoint + DB |
| E2E | Login → Suche → Ergebnis |

---

# ⚙️ Konfiguration (`.env`)

```env
APP_PASSWORD=secret
DATABASE_URL=sqlite:///./dufour.db
```

Niemals hardcoden. Immer über `python-dotenv` laden.

---

# 📦 Dependencies (`requirements.txt`)

```
fastapi
uvicorn
sqlalchemy
beautifulsoup4
python-dotenv
pytest
httpx
```

Dev-only (zukünftig in `requirements-dev.txt`):
```
black
ruff
isort
```

---

# 🚀 Projekt starten

```bash
# 1. Virtual Environment
python -m venv .venv
source .venv/bin/activate.fish        # Linux/macOS
.venv\Scripts\activate           # Windows

# 2. Dependencies
pip install -r requirements.txt

# 3. .env anlegen
echo "APP_PASSWORD=secret" > .env

# 4. HTML-Dateien parsen
python scripts/parse_html.py

# 5. Server starten
uvicorn backend.main:app --reload

# 6. Tests
pytest
```

---

# 🗃️ Git & Datenstrategie

```gitignore
data/        # HTML-Rohdaten – nicht im Repo
.env         # Secrets – niemals committen
*.db         # Datenbank – lokal oder via SCP auf Server
.venv/
__pycache__/
```

**Deployment-Workflow:**
```
Lokal:  python scripts/parse_html.py → dufour.db erzeugen
        scp dufour.db user@server:/pfad/projekt/
Server: git pull → uvicorn starten
```

---

# ✅ Allgemeine Prinzipien

- Lesbarkeit vor Cleverness
- Explizit vor implizit
- Funktionen klein und fokussiert halten
- Keine unnötigen Abstraktionen
- Jedes Feature hat Tests
- Max. 50 Zeilen pro Commit
- Conventional Commits Format verwenden
