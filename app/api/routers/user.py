import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import createToken, decodeToken
from app.db.database import get_db
from app.models.user import User
from app.models.social_account import SocialAccount
from app.schemas.user import KakaoCallbackReq, LoginReq, LoginRes, MeRes, SignUpReq, SignUpRes
from app.schemas.response import ApiResponse
from app.services import kakao

router = APIRouter(prefix="/user", tags=["user"])
logger = logging.getLogger(__name__)
KAKAO_STATE_COOKIE = "KAKAO_OAUTH_STATE"
KAKAO_STATE_TTL_SECONDS = 300


def _kakao_is_configured() -> bool:
    return bool(settings.KAKAO_REST_API_KEY and settings.KAKAO_REDIRECT_URI)


def _kakao_error(response: Response, status_code: int, code: str):
    response.status_code = status_code
    return ApiResponse(code=status_code, message=code, result=None)


def _set_auth_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        "EN_AT",
        createToken(user_id),
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=1800,
    )


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
        createToken(user.idx),
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=1800,
    )
    return ApiResponse(code=200, message="로그인되었습니다.", result=user)

@router.get("/me", response_model=ApiResponse[MeRes])
def me(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("EN_AT")
    try:
        if not token:
            raise ValueError("Missing session token")
        user = db.get(User, decodeToken(token))
        if user is None:
            raise ValueError("Session user no longer exists")
    except ValueError:
        cleared_cookie = Response()
        cleared_cookie.delete_cookie(
            "EN_AT",
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
            headers={"Set-Cookie": cleared_cookie.headers["set-cookie"]},
        )

    display_kind = "email" if user.email else "nickname"
    display_name = user.email or user.name
    return ApiResponse(
        code=200,
        message="현재 로그인 사용자입니다.",
        result=MeRes(display_name=display_name, display_kind=display_kind),
    )

@router.get("/oauth/kakao/state")
def kakao_oauth_state(response: Response):
    if not _kakao_is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="provider_unavailable",
        )

    state = secrets.token_urlsafe(32)
    response.set_cookie(
        KAKAO_STATE_COOKIE,
        state,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=KAKAO_STATE_TTL_SECONDS,
    )
    return ApiResponse(
        code=200,
        message="OAuth state created.",
        result={"state": state},
    )


def _resolve_kakao_user(db: Session, provider_user_id: str, nickname: str) -> User:
    account = db.scalar(
        select(SocialAccount).where(
            SocialAccount.provider == "kakao",
            SocialAccount.provider_user_id == provider_user_id,
        )
    )
    if account is not None:
        user = db.get(User, account.user_id)
        if user is None:
            raise kakao.KakaoProviderError(
                "Kakao identity references a missing user", stage="identity_resolution"
            )
        if user.name != nickname:
            user.name = nickname
            db.commit()
        return user

    user = User(email=None, password=None, name=nickname)
    db.add(user)
    try:
        db.flush()
        db.add(SocialAccount(
            user_id=user.idx,
            provider="kakao",
            provider_user_id=provider_user_id,
        ))
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as exc:
        db.rollback()
        account = db.scalar(
            select(SocialAccount).where(
                SocialAccount.provider == "kakao",
                SocialAccount.provider_user_id == provider_user_id,
            )
        )
        if account is None:
            raise kakao.KakaoProviderError(
                "Kakao identity could not be created", stage="identity_resolution"
            ) from exc
        user = db.get(User, account.user_id)
        if user is None:
            raise kakao.KakaoProviderError(
                "Kakao identity references a missing user", stage="identity_resolution"
            ) from exc
        if user.name != nickname:
            user.name = nickname
            db.commit()
        return user


@router.post("/oauth/kakao/callback")
def kakao_oauth_callback(
    req: KakaoCallbackReq,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    state_cookie = request.cookies.get(KAKAO_STATE_COOKIE)
    response.delete_cookie(
        KAKAO_STATE_COOKIE,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )
    if not req.state or not state_cookie or not secrets.compare_digest(req.state, state_cookie):
        return _kakao_error(response, status.HTTP_400_BAD_REQUEST, "invalid_state")
    if req.error:
        return _kakao_error(response, status.HTTP_400_BAD_REQUEST, "cancelled")
    if not req.code:
        return _kakao_error(response, status.HTTP_400_BAD_REQUEST, "invalid_request")
    if not _kakao_is_configured():
        return _kakao_error(response, status.HTTP_503_SERVICE_UNAVAILABLE, "provider_unavailable")

    try:
        access_token = kakao.exchange_code(req.code, settings.KAKAO_REDIRECT_URI)
        profile = kakao.fetch_profile(access_token)
        if not profile.nickname.strip():
            return _kakao_error(response, status.HTTP_400_BAD_REQUEST, "nickname_required")
        user = _resolve_kakao_user(db, profile.user_id, profile.nickname.strip())
    except kakao.KakaoProviderError as exc:
        logger.warning(
            "Kakao OAuth callback failed during %s "
            "(provider_status=%s provider_code=%s)",
            exc.stage,
            exc.provider_status,
            exc.provider_code,
        )
        return _kakao_error(response, status.HTTP_502_BAD_GATEWAY, "provider_error")

    _set_auth_cookie(response, user.idx)
    return ApiResponse(
        code=200,
        message="Kakao login successful.",
        result={"display_name": user.name, "display_kind": "nickname"},
    )
