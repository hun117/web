import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.database import Base, get_db
from app.main import app
from app.models import Course, CourseEnrollment, PaymentOrder, User


@pytest.fixture
def payment_client(monkeypatch):
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

    monkeypatch.setattr(settings, "PORTONE_STORE_ID", "store-test", raising=False)
    monkeypatch.setattr(settings, "PORTONE_CHANNEL_KEY", "channel-test", raising=False)
    monkeypatch.setattr(settings, "PORTONE_API_SECRET", "secret-test", raising=False)
    app.dependency_overrides[get_db] = override_get_db
    with session_local() as db:
        db.add_all([
            User(email="learner@example.com", password="password", name="Learner"),
            User(email="other@example.com", password="password", name="Other"),
            Course(
                title="파이썬 웹 개발",
                description="FastAPI 과정",
                instructor="김민준",
                category="개발",
                price=49000,
                thumbnail="",
                level="입문",
                duration="12시간",
                rating=4.8,
            ),
        ])
        db.commit()
    try:
        with TestClient(app) as client:
            yield client, session_local
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _login(client, email="learner@example.com"):
    response = client.post("/user/login", json={"email": email, "password": "password"})
    assert response.status_code == 200


def _create_order(client):
    return client.post("/payments/orders", json={"course_id": 1})


def test_payment_order_requires_login(payment_client):
    client, _ = payment_client

    response = _create_order(client)

    assert response.status_code == 401


def test_payment_order_uses_database_price_and_returns_public_portone_config(payment_client):
    client, session_local = payment_client
    _login(client)

    response = client.post("/payments/orders", json={"course_id": 1, "amount": 1})

    assert response.status_code == 200
    order = response.json()["result"]
    assert order["amount"] == 49000
    assert order["currency"] == "KRW"
    assert order["store_id"] == "store-test"
    assert order["channel_key"] == "channel-test"
    assert order["payment_id"].startswith("course-")
    with session_local() as db:
        saved = db.scalar(select(PaymentOrder).where(PaymentOrder.payment_id == order["payment_id"]))
        assert saved.amount == 49000
        assert saved.status == "PENDING"


def test_payment_completion_checks_portone_paid_status_and_exact_amount(payment_client, monkeypatch):
    client, session_local = payment_client
    _login(client)
    order = _create_order(client).json()["result"]
    calls = []

    def fake_get(url, headers, timeout):
        calls.append((url, headers, timeout))
        return httpx.Response(200, request=httpx.Request("GET", url), json={
            "id": order["payment_id"],
            "storeId": "store-test",
            "status": "PAID",
            "currency": "KRW",
            "amount": {"total": 1},
        })

    monkeypatch.setattr("app.api.routers.payments.httpx.get", fake_get)

    response = client.post("/payments/complete", json={"payment_id": order["payment_id"]})

    assert response.status_code == 400
    assert response.json()["code"] == 400
    assert calls[0][1]["Authorization"] == "PortOne secret-test"
    assert "secret-test" not in response.text
    with session_local() as db:
        assert db.scalar(select(func.count()).select_from(CourseEnrollment)) == 0


def test_payment_completion_creates_enrollment_only_once(payment_client, monkeypatch):
    client, session_local = payment_client
    _login(client)
    order = _create_order(client).json()["result"]

    def fake_get(url, headers, timeout):
        return httpx.Response(200, request=httpx.Request("GET", url), json={
            "id": order["payment_id"],
            "storeId": "store-test",
            "status": "PAID",
            "currency": "KRW",
            "amount": {"total": order["amount"]},
        })

    monkeypatch.setattr("app.api.routers.payments.httpx.get", fake_get)
    payload = {"payment_id": order["payment_id"]}

    first = client.post("/payments/complete", json=payload)
    second = client.post("/payments/complete", json=payload)

    assert first.status_code == 200
    assert first.json()["result"]["course_id"] == 1
    assert second.status_code == 200
    duplicate_order = client.post("/payments/orders", json={"course_id": 1})
    assert duplicate_order.status_code == 409
    assert client.get("/courses/1").json()["result"]["is_enrolled"] is True
    with session_local() as db:
        assert db.scalar(select(func.count()).select_from(CourseEnrollment)) == 1
        assert db.get(PaymentOrder, 1).status == "PAID"


def test_payment_order_is_bound_to_authenticated_user(payment_client, monkeypatch):
    client, _ = payment_client
    _login(client)
    order = _create_order(client).json()["result"]
    _login(client, "other@example.com")
    called = False

    def fake_get(*args, **kwargs):
        nonlocal called
        called = True
        return httpx.Response(200, json={})

    monkeypatch.setattr("app.api.routers.payments.httpx.get", fake_get)

    response = client.post("/payments/complete", json={"payment_id": order["payment_id"]})

    assert response.status_code == 404
    assert not called
