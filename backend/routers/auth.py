import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.database import get_session
from backend.dependencies import SECRET_KEY, ALGORITHM, get_current_user
from backend.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REMEMBER_ME_DAYS = 30


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

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def _set_auth_cookie(response: Response, token: str, remember_me: bool) -> None:
    max_age = 60 * 60 * 24 * REMEMBER_ME_DAYS if remember_me else None
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
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=body.name,
        email=body.email,
        hashed_password=pwd_context.hash(body.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserOut(id=user.id, name=user.name, email=user.email, role=user.role)


@router.post("/login", response_model=UserOut)
def login(body: LoginRequest, response: Response, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not pwd_context.verify(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.id)
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
