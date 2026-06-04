import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()

router = APIRouter()


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(request: LoginRequest):
    """Prüft das Passwort und setzt bei Erfolg ein Session-Cookie."""
    app_password = os.getenv("APP_PASSWORD")

    if not app_password or request.password != app_password:
        raise HTTPException(status_code=401, detail="Falsches Passwort")

    response = JSONResponse(content={"message": "Erfolgreich eingeloggt"})
    response.set_cookie(key="session", value="authenticated", httponly=True)
    return response