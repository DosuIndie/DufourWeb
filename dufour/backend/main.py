import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from backend.database import create_all
from backend.routers import search, auth

app = FastAPI()


def require_auth(request: Request):
    """Dependency, die prüft ob ein gültiger Session-Cookie vorhanden ist."""
    if request.cookies.get("session") != "authenticated":
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")


# Router einbinden (search-Router benötigt Auth) — MUSS vor dem Static-Mount kommen,
# damit /search und /login von der API beantwortet werden und nicht von StaticFiles.
app.include_router(search.router, dependencies=[__import__("fastapi").Depends(require_auth)])
app.include_router(auth.router)

# Frontend (login.html, search.html) als statische Dateien ausliefern
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend"), html=True), name="frontend")