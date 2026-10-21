# 환경 설정 파일 : DB 접속 주소, 토큰 시크릿 등 환경변수로 설정된 값을 불러오는 파일

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    SECRET_KEY:   str = Field(min_length=32)
    ALGORITHM:    str = "HS256"
    DATABASE_URL :str = "sqlite:///db.sqlite"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    KAKAO_REST_API_KEY: str = ""
    KAKAO_CLIENT_SECRET: str | None = None
    KAKAO_REDIRECT_URI: str = ""
    FRONTEND_URL: str = "http://127.0.0.1:5173"
    PORTONE_STORE_ID: str = ""
    PORTONE_CHANNEL_KEY: str = ""
    PORTONE_API_SECRET: str = ""

settings = Settings()
