from uuid import uuid4


def test_create_capture_api(test_client):
    response = test_client.post("/api/v1/captures", json={"content": "API test capture"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["content"] == "API test capture"
    assert "created_at" in data


def test_get_capture_api(test_client):
    # First create
    create_response = test_client.post("/api/v1/captures", json={"content": "Fetch me"})
    capture_id = create_response.json()["id"]

    # Then fetch
    get_response = test_client.get(f"/api/v1/captures/{capture_id}")
    assert get_response.status_code == 200
    assert get_response.json()["content"] == "Fetch me"


def test_get_capture_not_found(test_client):
    random_id = str(uuid4())
    response = test_client.get(f"/api/v1/captures/{random_id}")
    assert response.status_code == 404
