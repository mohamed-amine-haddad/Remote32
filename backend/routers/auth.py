from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.models import User
import backend.services.auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------- Schemas ----------

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str


# ---------- Helpers ----------

def _set_auth_cookie(response: Response, token: str, remember_me: bool) -> None:
    max_age = 60 * 60 * 24 * auth_service.REMEMBER_ME_DAYS if remember_me else None
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,       # JS cannot read this cookie
        samesite="lax",      # safe default; works via Vite proxy (same-origin in dev)
        secure=False,        # set True in production when served over HTTPS
        max_age=max_age,     # None = session cookie (expires when browser closes)
    )


# ---------- Endpoints ----------

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, session: Session = Depends(get_session)):
    try:
        user = auth_service.register_user(session, body.name, body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return UserOut(id=user.id, name=user.name, email=user.email, role=user.role)


@router.post("/login", response_model=UserOut)
def login(body: LoginRequest, response: Response, session: Session = Depends(get_session)):
    try:
        user = auth_service.authenticate_user(session, body.email, body.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_service.create_access_token(user.id)
    _set_auth_cookie(response, token, body.remember_me)
    return UserOut(id=user.id, name=user.name, email=user.email, role=user.role)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", samesite="lax")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
    )
