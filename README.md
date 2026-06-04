# Dufour Bible Topic Search

A lightweight web application for searching Bible references by topic. Authenticated users can enter a theological theme and receive matching Bible verses grouped into four categories.

## What it does

The app parses a collection of HTML source files, extracts Bible references, and stores them in a SQLite database. Through a simple web interface, users can search for topics and get results organised by:

- Altes Testament (Old Testament)
- Propheten (Prophets)
- Neues Testament (New Testament)
- Evangelien (Gospels)

Access is protected by a single password login. There is no user management — one shared password for all users.

## Project structure

```
backend/
├── main.py          # FastAPI entry point, route registration, static file serving
├── database.py      # SQLAlchemy + SQLite setup, session management
├── models.py        # ORM models: Topic, BibleReference
└── routers/
    ├── search.py    # GET /search?q= endpoint
    └── auth.py      # POST /login endpoint
frontend/
├── index.html       # Redirects to login
├── login.html       # Password login page
└── search.html      # Search interface with categorised results
data/                # HTML source files (not in repo — see Data Pipeline)
scripts/
└── parse_html.py    # Parses HTML files and writes to SQLite
tests/
├── test_models.py
├── test_auth.py
├── test_parser.py
└── test_search.py
.env                 # Local secrets (never commit)
.gitignore
requirements.txt
```

## UML

```mermaid
graph TD
    subgraph FRONTEND["Frontend (static HTML)"]
        LOGIN["login.html Password form"]
        SEARCH["search.html Topic search"]
    end

    subgraph ENV[".env"]
        ENVFILE["APP_PASSWORD=secret DATABASE_URL=postgresql://..."]
    end

    subgraph BACKEND["Backend (FastAPI)"]
        MAIN["main.py FastAPI app + static mount"]

        subgraph ROUTERS["Routers"]
            AUTH["routers/auth.py POST /login"]
            SRCH["routers/search.py GET /search"]
        end

        subgraph CORE["Core"]
            DB["database.py SQLAlchemy engine + session"]
            MDL["models.py Topic · BibleReference"]
        end
    end

    subgraph TESTS["Tests (pytest + httpx)"]
        TAUTH["test_auth.py"]
        TSRCH["test_search.py"]
    end

    subgraph PERSISTENCE["Persistence"]
        PG["PostgreSQL Render.com"]
        SQLITE["SQLite fallback"]
    end

    LOGIN  -->|"POST /login"| AUTH
    SEARCH -->|"GET /search"| SRCH

    MAIN --> AUTH
    MAIN --> SRCH

    AUTH --> DB
    SRCH --> MDL
    MDL  --> DB

    DB -->|"DATABASE_URL"| PG
    DB -->|"fallback if no env"| SQLITE

    TAUTH --> AUTH
    TSRCH --> SRCH

    ENVFILE -->|"loaded via python-dotenv"| DB
    ENVFILE -->|"loaded via python-dotenv"| AUTH

```

## Database schema

Two tables with a one-to-many relationship:

**topics**

```mermaid
erDiagram

    TOPICS {
        int id PK
        string name "unique, not null"
    }

    BIBLE_REFERENCES {
        int id PK
        string reference "not null"
        string category "not null"
        int topic_id FK "→ topics.id, cascade delete"
    }

    TOPICS ||--o{ BIBLE_REFERENCES : "1 has n"
```

## Setup

**1. Clone and create a virtual environment**

```bash
git clone <repo-url>
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Create `.env`**

```env
APP_PASSWORD=your_password_here
DATABASE_URL=sqlite:///./dufour.db
```

**4. Add HTML source files**

Place the HTML topic files into the `data/` directory. Or use the data in the repository.

**5. Parse HTML and populate the database**

```bash
python scripts/parse_html.py
```

This reads all `.html` files from `data/`, extracts Bible references using regex matching against a catalogue of German Bible book abbreviations, classifies each reference into one of the four categories, and writes everything to `dufour.db`.

**6. Start the server**

```bash
uvicorn backend.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) — you will be redirected to the login page.

## API

**`POST /login`**

```json
{ "password": "your_password" }
```

Returns a `session=authenticated` cookie on success. All subsequent requests must include this cookie.

**`GET /search?q=<topic>`**

Case-insensitive partial match against topic names. Returns:

```json
{
  "topic": "Glaube",
  "results": {
    "Altes Testament": ["Gen 15,6"],
    "Propheten": [],
    "Neues Testament": ["Röm 3,28", "Hebr 11,1"],
    "Evangelien": ["Joh 3,16"]
  }
}
```

Requires the session cookie. Returns `401` if not authenticated.

## Data pipeline

```
data/*.html
    └── BeautifulSoup4 parser
        └── Regex match against German Bible abbreviations
            └── Classify by book (Evangelien / NT / Propheten / AT)
                └── Deduplicate
                    └── Write to SQLite via SQLAlchemy
```

The parser handles both UTF-8 and Latin-1 encoded files. Multi-word abbreviations (e.g. `1 Petr`, `2 Kor`) are matched before single-word ones to avoid partial matches.

## Running tests

```bash
pytest
```

Tests cover models, authentication, the HTML parser, and the search endpoint.

## Deployment

The database is generated locally and copied to the server manually:

```bash
python scripts/parse_html.py       # generate dufour.db locally
scp dufour.db user@server:/path/to/dufour/
ssh user@server "cd /path/to/dufour && git pull && uvicorn backend.main:app"
```

`dufour.db` is intentionally excluded from the repository.

## Dependencies

```
fastapi
uvicorn
sqlalchemy
beautifulsoup4
python-dotenv
pytest
httpx
```
