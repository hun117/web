from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import createToken
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import LoginReq, LoginRes, SignUpReq, SignUpRes
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/signup", response_model=ApiResponse[SignUpRes])
def signup(req: SignUpReq, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == req.email))
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 가입된 이메일입니다.")

    new_user = User(email=req.email, password=req.password, name=req.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return ApiResponse(code=200, message="회원가입이 완료되었습니다.", result=new_user)


@router.post("/login", response_model=ApiResponse[LoginRes])
def login(req: LoginReq, res: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == req.email))
    if not user or user.password != req.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    res.set_cookie(
        "EN_AT",
        createToken(req.email),
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return ApiResponse(code=200, message="로그인되었습니다.", result=user)
