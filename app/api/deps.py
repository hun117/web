from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import decodeToken
from app.db.database import get_db
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("EN_AT")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")

    try:
        user = db.get(User, decodeToken(token))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.") from exc

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")
    return user


def get_optional_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    token = request.cookies.get("EN_AT")
    if not token:
        return None
    try:
        return db.get(User, decodeToken(token))
    except ValueError:
        return None
