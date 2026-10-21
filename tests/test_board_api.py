import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.models.board import Board


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client, TestingSessionLocal
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_board_list_converts_orm_rows_and_keeps_newest_first(client):
    test_client, session_local = client
    with session_local() as db:
        older = Board(title="older", contents="first")
        newer = Board(title="newer", contents="second")
        db.add_all([older, newer])
        db.commit()
        older_idx, newer_idx = older.idx, newer.idx

    response = test_client.get("/board/list")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["result"]["total"] == 2
    assert [item["idx"] for item in payload["result"]["items"]] == [newer_idx, older_idx]
    assert payload["result"]["items"][0] == {
        "idx": newer_idx,
        "title": "newer",
        "contents": "second",
    }


def test_board_list_returns_empty_result(client):
    test_client, _ = client

    response = test_client.get("/board/list")

    assert response.status_code == 200
    assert response.json()["result"] == {"items": [], "total": 0}


def test_board_read_converts_orm_row(client):
    test_client, session_local = client
    with session_local() as db:
        board = Board(title="stay", contents="by the sea")
        db.add(board)
        db.commit()
        board_idx = board.idx

    response = test_client.get(f"/board/read/{board_idx}")

    assert response.status_code == 200
    assert response.json()["result"] == {
        "idx": board_idx,
        "title": "stay",
        "contents": "by the sea",
    }


def test_board_read_missing_row_returns_404(client):
    test_client, _ = client

    response = test_client.get("/board/read/999")

    assert response.status_code == 404
    assert response.json()["code"] == 404


def test_board_register_converts_created_orm_row(client):
    test_client, _ = client

    response = test_client.post(
        "/board/rergister",
        json={"title": "weekend trip", "contents": "mountain cabin"},
    )

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["idx"] > 0
    assert result["title"] == "weekend trip"
    assert result["contents"] == "mountain cabin"
