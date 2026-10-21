import importlib
import importlib.util

import httpx
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.database import Base, get_db
from app.main import app
from app.models import SocialAccount, User


def _load_migrate_user_table():
    spec = importlib.util.find_spec("app.db.migrations")
    assert spec is not None, "app.db.migrations is not implemented"
    return importlib.import_module("app.db.migrations").migrate_user_table


def test_migrate_user_table_preserves_legacy_rows_and_is_repeatable():
    migrate_user_table = _load_migrate_user_table()
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE user ("
                "idx INTEGER PRIMARY KEY, email VARCHAR NOT NULL, "
                "password VARCHAR NOT NULL, name VARCHAR NOT NULL)"
            ))
            connection.execute(text(
                "INSERT INTO user (idx, email, password, name) "
                "VALUES (42, 'reader@example.com', 'secret', 'Reader')"
            ))

        migrate_user_table(engine)
        migrate_user_table(engine)

        with engine.connect() as connection:
            rows = connection.execute(
                text("SELECT idx, email, password, name FROM user")
            ).all()
        assert rows == [(42, "reader@example.com", "secret", "Reader")]

        columns = {column["name"]: column for column in inspect(engine).get_columns("user")}
        assert columns["email"]["nullable"] is True
        assert columns["password"]["nullable"] is True
    finally:
        engine.dispose()


def test_migrate_user_table_is_safe_before_create_all_on_empty_database():
    migrate_user_table = _load_migrate_user_table()
    from app.db.database import Base
    from app.models.board import Board
    from app.models.user import User
    import app.models.social_account  # noqa: F401

    engine = create_engine("sqlite://")
    try:
        migrate_user_table(engine)
        Base.metadata.create_all(engine)
        assert inspect(engine).has_table("user")
        assert inspect(engine).has_table("social_account")
    finally:
        engine.dispose()


@pytest.fixture
def user_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autoflush=False, bind=engine)

    def override_get_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client, session_local
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_password_login_token_subject_is_the_local_user_id(user_client):
    client, session_local = user_client
    with session_local() as db:
        user = User(email="reader@example.com", password="secret", name="Reader")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.idx

    response = client.post(
        "/user/login",
        json={"email": "reader@example.com", "password": "secret"},
    )

    assert response.status_code == 200
    token = response.cookies["EN_AT"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == str(user_id)


def test_me_returns_email_for_password_user_and_nickname_for_social_user(user_client):
    client, session_local = user_client
    with session_local() as db:
        password_user = User(email="reader@example.com", password="secret", name="Reader")
        social_user = User(email=None, password=None, name="Kakao Nick")
        db.add_all([password_user, social_user])
        db.commit()
        db.refresh(password_user)
        db.refresh(social_user)
        db.add(SocialAccount(
            user_id=social_user.idx,
            provider="kakao",
            provider_user_id="kakao-123",
        ))
        db.commit()
        password_id, social_id = password_user.idx, social_user.idx

    results = []
    for user_id in (password_id, social_id):
        client.cookies.set(
            "EN_AT",
            jwt.encode(
                {"sub": str(user_id), "exp": 4_102_444_800},
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM,
            ),
        )
        response = client.get("/user/me")
        assert response.status_code == 200
        results.append(response.json()["result"])

    assert results == [
        {"display_name": "reader@example.com", "display_kind": "email"},
        {"display_name": "Kakao Nick", "display_kind": "nickname"},
    ]


@pytest.mark.parametrize("token_kind", ["missing", "malformed", "expired", "deleted_user"])
def test_me_rejects_invalid_sessions_and_clears_cookie(user_client, token_kind):
    client, session_local = user_client
    if token_kind == "missing":
        token = None
    elif token_kind == "malformed":
        token = "not-a-jwt"
    elif token_kind == "expired":
        token = jwt.encode(
            {"sub": "1", "exp": 1},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
    else:
        token = jwt.encode(
            {"sub": "99999", "exp": 4_102_444_800},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    if token is not None:
        client.cookies.set("EN_AT", token)
    response = client.get("/user/me")

    assert response.status_code == 401
    set_cookie = response.headers.get("set-cookie", "").lower()
    assert set_cookie.startswith('en_at="";')
    assert "max-age=0" in set_cookie


def test_existing_signup_and_password_login_contract_stays_available(user_client):
    client, _ = user_client

    signup = client.post(
        "/user/signup",
        json={"email": "member@example.com", "password": "secret", "name": "Member"},
    )
    login = client.post(
        "/user/login",
        json={"email": "member@example.com", "password": "secret"},
    )

    assert signup.status_code == 200
    assert signup.json()["result"]["email"] == "member@example.com"
    assert login.status_code == 200
    assert login.json()["result"]["email"] == "member@example.com"


def _load_kakao_service():
    spec = importlib.util.find_spec("app.services.kakao")
    assert spec is not None, "app.services.kakao is not implemented"
    return importlib.import_module("app.services.kakao")


def test_kakao_state_reports_missing_server_configuration(user_client, monkeypatch):
    client, _ = user_client
    from app.core.config import settings

    monkeypatch.setattr(settings, "KAKAO_REST_API_KEY", "")
    monkeypatch.setattr(settings, "KAKAO_REDIRECT_URI", "")

    response = client.get("/user/oauth/kakao/state")

    assert response.status_code == 503
    assert response.json()["message"] == "provider_unavailable"


def test_kakao_service_exchanges_code_and_returns_only_id_and_nickname(monkeypatch):
    service = _load_kakao_service()
    from app.core.config import settings

    monkeypatch.setattr(settings, "KAKAO_REST_API_KEY", "test-rest-key")
    monkeypatch.setattr(settings, "KAKAO_CLIENT_SECRET", "test-client-secret")
    original_client = httpx.Client

    def handler(request):
        if request.url.path == "/oauth/token":
            assert request.method == "POST"
            assert request.headers["content-type"].startswith(
                "application/x-www-form-urlencoded"
            )
            assert "client_id=test-rest-key" in request.content.decode()
            assert "client_secret=test-client-secret" in request.content.decode()
            return httpx.Response(200, json={"access_token": "provider-access-token"})
        assert request.url.path == "/v2/user/me"
        assert request.headers["authorization"] == "Bearer provider-access-token"
        return httpx.Response(200, json={
            "id": 987654,
            "kakao_account": {
                "profile": {"nickname": "Kakao Reader"},
                "email": "shared@example.com",
            },
        })

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        service.httpx,
        "Client",
        lambda **kwargs: original_client(transport=transport, **kwargs),
    )

    access_token = service.exchange_code(
        "authorization-code",
        "http://127.0.0.1:5173/login/kakao/callback",
    )
    profile = service.fetch_profile(access_token)

    assert access_token == "provider-access-token"
    assert profile.user_id == "987654"
    assert profile.nickname == "Kakao Reader"
    assert not hasattr(profile, "email")


def test_kakao_service_wraps_timeouts_and_rejects_malformed_profile(monkeypatch):
    service = _load_kakao_service()
    original_client = httpx.Client

    def timeout_handler(request):
        raise httpx.ReadTimeout("simulated timeout", request=request)

    timeout_transport = httpx.MockTransport(timeout_handler)
    monkeypatch.setattr(
        service.httpx,
        "Client",
        lambda **kwargs: original_client(transport=timeout_transport, **kwargs),
    )
    with pytest.raises(service.KakaoProviderError) as timeout_error:
        service.exchange_code("authorization-code", "http://example.test/callback")
    assert timeout_error.value.stage == "token_exchange"

    def malformed_profile_handler(request):
        if request.url.path == "/oauth/token":
            return httpx.Response(200, json={"access_token": "provider-token"})
        return httpx.Response(200, json={"id": "987654", "kakao_account": ["unexpected"]})

    malformed_transport = httpx.MockTransport(malformed_profile_handler)
    monkeypatch.setattr(
        service.httpx,
        "Client",
        lambda **kwargs: original_client(transport=malformed_transport, **kwargs),
    )
    with pytest.raises(service.KakaoProviderError) as profile_error:
        service.fetch_profile("provider-token")
    assert profile_error.value.stage == "profile_fetch"


def test_kakao_token_errors_keep_safe_provider_diagnostics(monkeypatch):
    service = _load_kakao_service()
    original_client = httpx.Client

    def unauthorized_handler(request):
        return httpx.Response(401, json={"error": "invalid_client"})

    transport = httpx.MockTransport(unauthorized_handler)
    monkeypatch.setattr(
        service.httpx,
        "Client",
        lambda **kwargs: original_client(transport=transport, **kwargs),
    )

    with pytest.raises(service.KakaoProviderError) as error:
        service.exchange_code("authorization-code", "http://example.test/callback")

    assert error.value.stage == "token_exchange"
    assert error.value.provider_status == 401
    assert error.value.provider_code == "invalid_client"


def test_kakao_callback_creates_and_reuses_independent_social_identity(
    user_client, monkeypatch
):
    client, session_local = user_client
    service = _load_kakao_service()
    from app.core.config import settings

    monkeypatch.setattr(settings, "KAKAO_REST_API_KEY", "test-rest-key")
    monkeypatch.setattr(
        settings,
        "KAKAO_REDIRECT_URI",
        "http://127.0.0.1:5173/login/kakao/callback",
    )
    monkeypatch.setattr(settings, "KAKAO_CLIENT_SECRET", None)
    with session_local() as db:
        db.add(User(email="shared@example.com", password="secret", name="Local"))
        db.commit()

    monkeypatch.setattr(service, "exchange_code", lambda code, redirect_uri: "mock-token")
    monkeypatch.setattr(
        service,
        "fetch_profile",
        lambda token: service.KakaoProfile(user_id="987654", nickname="Kakao Reader"),
    )

    for _ in range(2):
        state_response = client.get("/user/oauth/kakao/state")
        assert state_response.status_code == 200
        state = state_response.json()["result"]["state"]
        response = client.post(
            "/user/oauth/kakao/callback",
            json={"code": "authorization-code", "state": state},
        )
        assert response.status_code == 200
        assert response.json()["result"] == {
            "display_name": "Kakao Reader",
            "display_kind": "nickname",
        }

    with session_local() as db:
        users = db.query(User).order_by(User.idx).all()
        accounts = db.query(SocialAccount).all()
        assert len(users) == 2
        assert users[1].email is None
        assert users[1].password is None
        assert len(accounts) == 1
        assert accounts[0].provider_user_id == "987654"


def test_kakao_callback_cancellation_and_provider_failure_do_not_create_users(
    user_client, monkeypatch
):
    client, session_local = user_client
    service = _load_kakao_service()
    from app.core.config import settings

    monkeypatch.setattr(settings, "KAKAO_REST_API_KEY", "test-rest-key")
    monkeypatch.setattr(
        settings,
        "KAKAO_REDIRECT_URI",
        "http://127.0.0.1:5173/login/kakao/callback",
    )
    monkeypatch.setattr(settings, "KAKAO_CLIENT_SECRET", None)
    state = client.get("/user/oauth/kakao/state").json()["result"]["state"]
    cancelled = client.post(
        "/user/oauth/kakao/callback",
        json={"state": state, "error": "access_denied"},
    )
    assert cancelled.status_code == 400
    assert cancelled.json()["message"] == "cancelled"
    assert "kakao_oauth_state=\"\"" in cancelled.headers.get("set-cookie", "").lower()

    state = client.get("/user/oauth/kakao/state").json()["result"]["state"]
    monkeypatch.setattr(service, "exchange_code", lambda code, redirect_uri: (_ for _ in ()).throw(
        service.KakaoProviderError("provider error")
    ))
    failed = client.post(
        "/user/oauth/kakao/callback",
        json={"code": "authorization-code", "state": state},
    )
    assert failed.status_code == 502
    assert failed.json()["message"] == "provider_error"
    with session_local() as db:
        assert db.query(User).count() == 0


def test_kakao_callback_rejects_state_mismatch_and_missing_nickname(
    user_client, monkeypatch
):
    client, session_local = user_client
    service = _load_kakao_service()
    from app.core.config import settings

    monkeypatch.setattr(settings, "KAKAO_REST_API_KEY", "test-rest-key")
    monkeypatch.setattr(
        settings,
        "KAKAO_REDIRECT_URI",
        "http://127.0.0.1:5173/login/kakao/callback",
    )
    monkeypatch.setattr(settings, "KAKAO_CLIENT_SECRET", None)
    client.get("/user/oauth/kakao/state")
    mismatch = client.post(
        "/user/oauth/kakao/callback",
        json={"code": "authorization-code", "state": "wrong-state"},
    )
    assert mismatch.status_code == 400
    assert mismatch.json()["message"] == "invalid_state"

    state = client.get("/user/oauth/kakao/state").json()["result"]["state"]
    monkeypatch.setattr(service, "exchange_code", lambda code, redirect_uri: "mock-token")
    monkeypatch.setattr(
        service,
        "fetch_profile",
        lambda token: service.KakaoProfile(user_id="987654", nickname=""),
    )
    missing_nickname = client.post(
        "/user/oauth/kakao/callback",
        json={"code": "authorization-code", "state": state},
    )
    assert missing_nickname.status_code == 400
    assert missing_nickname.json()["message"] == "nickname_required"
    with session_local() as db:
        assert db.query(User).count() == 0
