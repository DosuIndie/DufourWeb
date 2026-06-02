from fastapi import FastAPI, Request, HTTPException
from backend.database import create_all
from backend.routers import search, auth

app = FastAPI()


def require_auth(request: Request):
    """Dependency, die prüft ob ein gültiger Session-Cookie vorhanden ist."""
    if request.cookies.get("session") != "authenticated":
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")


# Router einbinden (search-Router benötigt Auth)
app.include_router(search.router, dependencies=[__import__("fastapi").Depends(require_auth)])
app.include_router(auth.router)