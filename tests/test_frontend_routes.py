from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_frontend_routes_serve_vue_shell():
    for path in ("/", "/register", "/login", "/posts", "/posts/new", "/posts/12"):
        response = client.get(path)
        assert response.status_code == 200
        assert '<div id="app"></div>' in response.text


def test_unknown_frontend_route_returns_not_found():
    response = client.get("/not-a-page")
    assert response.status_code == 404
