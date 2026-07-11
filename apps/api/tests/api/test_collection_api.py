def test_collection_api_lifecycle(test_client):
    # 1. Create Collection
    res = test_client.post(
        "/api/v1/collections",
        json={"name": "DevSpace", "description": "Programming topics"},
    )
    assert res.status_code == 201
    data = res.json()
    col_id = data["id"]
    assert data["name"] == "DevSpace"

    # 2. Get Collection
    res = test_client.get(f"/api/v1/collections/{col_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "DevSpace"

    # 3. Update Collection
    res = test_client.patch(f"/api/v1/collections/{col_id}", json={"description": "Updated"})
    assert res.status_code == 200
    assert res.json()["description"] == "Updated"

    # 4. List Collections
    res = test_client.get("/api/v1/collections")
    assert res.status_code == 200
    assert len(res.json()) >= 1
    assert any(c["id"] == col_id for c in res.json())

    # 5. Memberships Endpoint Tests
    res_cap = test_client.post("/api/v1/captures", json={"content": "Member Capture"})
    cap_id = res_cap.json()["id"]

    res_add = test_client.post(
        f"/api/v1/collections/{col_id}/entities",
        json={"entity_id": cap_id, "entity_type": "Capture"},
    )
    assert res_add.status_code == 201

    # Get members of collection
    res_list = test_client.get(f"/api/v1/collections/{col_id}/entities")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
    assert res_list.json()[0]["id"] == cap_id

    # Get collections of entity
    res_entity_cols = test_client.get(f"/api/v1/collections/entity/{cap_id}")
    assert res_entity_cols.status_code == 200
    assert len(res_entity_cols.json()) == 1
    assert res_entity_cols.json()[0]["id"] == col_id

    # Delete blocked when non-empty
    res_del_err = test_client.delete(f"/api/v1/collections/{col_id}")
    assert res_del_err.status_code == 400

    # Remove entity membership
    res_rem = test_client.delete(f"/api/v1/collections/{col_id}/entities/{cap_id}")
    assert res_rem.status_code == 204

    # Delete collection should now succeed
    res_del = test_client.delete(f"/api/v1/collections/{col_id}")
    assert res_del.status_code == 204
