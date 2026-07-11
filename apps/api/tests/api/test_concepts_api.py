from uuid import uuid4


def test_create_concept_api(test_client):
    response = test_client.post(
        "/api/v1/concepts",
        json={"title": "API test concept", "summary": "API summary"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "API test concept"
    assert data["summary"] == "API summary"
    assert "created_at" in data
    assert "updated_at" in data


def test_get_concept_api(test_client):
    # First create
    create_response = test_client.post(
        "/api/v1/concepts",
        json={"title": "Fetch me", "summary": "Fetch summary"},
    )
    concept_id = create_response.json()["id"]

    # Then fetch
    get_response = test_client.get(f"/api/v1/concepts/{concept_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Fetch me"
    assert get_response.json()["summary"] == "Fetch summary"


def test_get_concept_not_found(test_client):
    random_id = str(uuid4())
    response = test_client.get(f"/api/v1/concepts/{random_id}")
    assert response.status_code == 404
