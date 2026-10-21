from dataclasses import dataclass

import httpx

from app.core.config import settings


class KakaoProviderError(Exception):
    """Raised when Kakao authentication or profile retrieval fails."""

    def __init__(
        self,
        message: str,
        *,
        stage: str = "provider",
        provider_status: int | None = None,
        provider_code: str | None = None,
    ):
        super().__init__(message)
        self.stage = stage
        self.provider_status = provider_status
        self.provider_code = provider_code


@dataclass(frozen=True)
class KakaoProfile:
    user_id: str
    nickname: str


def _provider_error(message: str, stage: str, exc: Exception) -> KakaoProviderError:
    response = getattr(exc, "response", None)
    provider_code = None
    if response is not None:
        try:
            payload = response.json()
        except ValueError:
            payload = None
        if isinstance(payload, dict):
            code = payload.get("error")
            if isinstance(code, str):
                provider_code = code[:80]

    return KakaoProviderError(
        message,
        stage=stage,
        provider_status=response.status_code if response is not None else None,
        provider_code=provider_code,
    )


def exchange_code(code: str, redirect_uri: str) -> str:
    form_data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_REST_API_KEY,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    if settings.KAKAO_CLIENT_SECRET:
        form_data["client_secret"] = settings.KAKAO_CLIENT_SECRET

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(
                "https://kauth.kakao.com/oauth/token",
                data=form_data,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise KakaoProviderError(
                    "Kakao token response was invalid",
                    stage="token_exchange",
                    provider_status=response.status_code,
                )
            access_token = payload.get("access_token")
    except (httpx.HTTPError, ValueError) as exc:
        raise _provider_error("Kakao token exchange failed", "token_exchange", exc) from exc

    if not isinstance(access_token, str) or not access_token:
        raise KakaoProviderError(
            "Kakao token response was invalid",
            stage="token_exchange",
            provider_status=response.status_code,
        )
    return access_token


def fetch_profile(access_token: str) -> KakaoProfile:
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise _provider_error("Kakao profile request failed", "profile_fetch", exc) from exc

    if not isinstance(payload, dict):
        raise KakaoProviderError(
            "Kakao profile response was invalid",
            stage="profile_fetch",
            provider_status=response.status_code,
        )
    user_id = payload.get("id")
    kakao_account = payload.get("kakao_account") or {}
    if not isinstance(kakao_account, dict):
        raise KakaoProviderError(
            "Kakao account response was invalid",
            stage="profile_fetch",
            provider_status=response.status_code,
        )
    profile = kakao_account.get("profile") or {}
    if not isinstance(profile, dict):
        raise KakaoProviderError(
            "Kakao profile response was invalid",
            stage="profile_fetch",
            provider_status=response.status_code,
        )
    nickname = profile.get("nickname")
    if user_id is None or not isinstance(nickname, str) or not nickname.strip():
        raise KakaoProviderError(
            "Kakao profile is missing required nickname data",
            stage="profile_fetch",
            provider_status=response.status_code,
        )

    return KakaoProfile(user_id=str(user_id), nickname=nickname.strip())
