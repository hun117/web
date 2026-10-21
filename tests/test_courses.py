from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_course_catalog_lists_seeded_courses_with_summary_fields():
    response = client.get("/courses")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["result"]["total"] >= 1
    course = body["result"]["items"][0]
    assert {"id", "title", "description", "instructor", "category", "price", "thumbnail", "level", "duration", "rating"} <= course.keys()


def test_course_detail_returns_matching_course():
    listed = client.get("/courses").json()["result"]["items"][0]

    response = client.get(f"/courses/{listed['id']}")

    assert response.status_code == 200
    assert response.json()["result"]["id"] == listed["id"]
    assert response.json()["result"]["title"] == listed["title"]
    assert response.json()["result"]["is_enrolled"] is False


def test_missing_course_returns_api_response_404():
    response = client.get("/courses/2147483647")

    assert response.status_code == 404
    assert response.json()["code"] == 404
    assert response.json()["result"] is None


def test_courses_openapi_documents_catalog_contract():
    schema = client.get("/openapi.json").json()
    assert "/courses" in schema["paths"]
    assert "/courses/{course_id}" in schema["paths"]
