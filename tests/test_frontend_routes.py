import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_backend_does_not_serve_frontend_routes_or_assets():
    for path in ("/", "/register", "/login", "/posts", "/course/12", "/static/index.html"):
        response = client.get(path)
        assert response.status_code == 404


@pytest.mark.parametrize(
    "origin",
    [
        "http://localhost:5173",
        "https://www.pepepe.p-e.kr",
        "http://www.pepepe.p-e.kr",
    ],
)
def test_cors_allows_the_frontend_origin_and_cookie_credentials(origin):
    response = client.options(
        "/courses",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"
