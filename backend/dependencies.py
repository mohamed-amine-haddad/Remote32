import os
from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlmodel import Session

from backend.database import get_session
from backend.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"


def get_current_user(
    access_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session),
) -> User:
    not_authenticated = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    if access_token is None:
        raise not_authenticated
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise not_authenticated
    except JWTError:
        raise not_authenticated

    user = session.get(User, int(user_id))
    if user is None:
        raise not_authenticated
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user
