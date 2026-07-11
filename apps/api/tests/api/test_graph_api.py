def test_graph_api(test_client):
    res_c1 = test_client.post("/api/v1/captures", json={"content": "C1"})
    id1 = res_c1.json()["id"]

    res_c2 = test_client.post("/api/v1/captures", json={"content": "C2"})
    id2 = res_c2.json()["id"]

    test_client.post(
        "/api/v1/relationships",
        json={
            "from_id": id1,
            "from_type": "Capture",
            "to_id": id2,
            "to_type": "Capture",
            "relationship_type": "RELATED_TO",
        },
    )

    # Test entity endpoints
    res = test_client.get(f"/api/v1/graph/entity/{id1}")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == id2

    # Test neighborhood endpoint
    res = test_client.get(f"/api/v1/graph/neighborhood/{id1}")
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) == 2
    assert len(data["relationships"]) == 1

    # Test path-preview endpoint
    res = test_client.get(f"/api/v1/graph/path-preview/{id1}")
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) == 2
    assert len(data["relationships"]) == 1
