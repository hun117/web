# 보안상 중요한 값이나 기능들을 모아둔 파일. 토큰 생성, 비밀번호 암호화 등

import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings


def createToken(userId: int):
    payload = {
        "sub": str(userId),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodeToken(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid session token") from exc


#  토큰 확인하는 함수
#  토큰에서 원하는 값을 가져오는 함수
# 비밀번호를 암호화 하는 함수
# 비밀번호 확인
