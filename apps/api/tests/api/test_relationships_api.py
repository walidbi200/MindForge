def test_relationships_crud_api(test_client):
    # 1. Create two captures
    res_c1 = test_client.post("/api/v1/captures", json={"content": "C1"})
    assert res_c1.status_code == 201
    id1 = res_c1.json()["id"]

    res_c2 = test_client.post("/api/v1/captures", json={"content": "C2"})
    assert res_c2.status_code == 201
    id2 = res_c2.json()["id"]

    # 2. Create relationship
    res_rel = test_client.post(
        "/api/v1/relationships",
        json={
            "from_id": id1,
            "from_type": "Capture",
            "to_id": id2,
            "to_type": "Capture",
            "relationship_type": "RELATED_TO",
        },
    )
    assert res_rel.status_code == 201
    rel_id = res_rel.json()["id"]

    # 3. Get relationship
    res_get = test_client.get(f"/api/v1/relationships/{rel_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == rel_id

    # 4. List outgoing
    res_out = test_client.get(f"/api/v1/relationships/entity/{id1}/outgoing")
    assert res_out.status_code == 200
    assert len(res_out.json()) == 1
    assert res_out.json()[0]["id"] == rel_id

    # 5. List incoming
    res_in = test_client.get(f"/api/v1/relationships/entity/{id2}/incoming")
    assert res_in.status_code == 200
    assert len(res_in.json()) == 1
    assert res_in.json()[0]["id"] == rel_id

    # 6. Delete relationship
    res_del = test_client.delete(f"/api/v1/relationships/{rel_id}")
    assert res_del.status_code == 204

    # 7. Verify deletion
    assert test_client.get(f"/api/v1/relationships/{rel_id}").status_code == 404
