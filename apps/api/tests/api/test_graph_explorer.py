from fastapi.testclient import TestClient


def test_get_knowledge_neighborhood(test_client: TestClient):
    res_c1 = test_client.post("/api/v1/concepts", json={"title": "Test Concept 1", "summary": "Summary 1"})
    id1 = res_c1.json()["id"]

    res_c2 = test_client.post("/api/v1/concepts", json={"title": "Test Concept 2", "summary": "Summary 2"})
    id2 = res_c2.json()["id"]

    test_client.post(
        "/api/v1/relationships",
        json={
            "from_id": id1,
            "from_type": "Concept",
            "to_id": id2,
            "to_type": "Concept",
            "relationship_type": "RELATED_TO",
        },
    )

    res = test_client.get(f"/api/v1/graph/neighborhood/{id1}")
    assert res.status_code == 200
    data = res.json()
    assert "center" in data
    assert data["center"]["id"] == id1
    assert data["center"]["entity_type"] == "Concept"
    assert "concepts" in data
    assert len(data["concepts"]) == 1
    assert data["concepts"][0]["id"] == id2
    assert "relationships" in data


def test_check_duplicates(test_client: TestClient):
    res_c1 = test_client.post("/api/v1/concepts", json={"title": "Unique Concept A", "summary": "Summary 1"})
    id1 = res_c1.json()["id"]

    # Exact match
    res = test_client.get("/api/v1/graph/check-duplicates?title=Unique Concept A")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["concept_id"] == id1

    # With exclude_id
    res = test_client.get(f"/api/v1/graph/check-duplicates?title=Unique Concept A&exclude_id={id1}")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 0


def test_timeline_filters(test_client: TestClient):
    test_client.post("/api/v1/captures", json={"content": "Timeline capture"})

    # Filter by aggregate_type
    res = test_client.get("/api/v1/timeline?aggregate_type=Capture")
    assert res.status_code == 200
    data = res.json()
    for e in data:
        assert e["aggregate_type"] == "Capture"

    # Filter by event_type
    res = test_client.get("/api/v1/timeline?event_type=CaptureCreated")
    assert res.status_code == 200
    data = res.json()
    for e in data:
        assert e["event_type"] == "CaptureCreated"
