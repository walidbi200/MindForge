from datetime import datetime, timedelta, timezone


def test_review_lifecycle(test_client):
    # 1. Create Capture
    res_cap = test_client.post("/api/v1/captures", json={"content": "Capture for review"})
    cap_id = res_cap.json()["id"]

    # 2. Create Review
    due_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    res_rev = test_client.post(
        "/api/v1/reviews", json={"entity_id": cap_id, "entity_type": "Capture", "due_at": due_at}
    )
    assert res_rev.status_code == 201
    rev_id = res_rev.json()["id"]

    # 3. Check duplicate pending blocked
    res_dup = test_client.post(
        "/api/v1/reviews", json={"entity_id": cap_id, "entity_type": "Capture", "due_at": due_at}
    )
    assert res_dup.status_code == 409

    # 4. List Due
    res_due = test_client.get("/api/v1/reviews/due")
    assert res_due.status_code == 200
    assert any(r["id"] == rev_id for r in res_due.json())

    # 5. List Entity Reviews
    res_ent = test_client.get(f"/api/v1/reviews/entity/{cap_id}")
    assert res_ent.status_code == 200
    assert len(res_ent.json()) == 1

    # 6. Complete
    res_comp = test_client.post(f"/api/v1/reviews/{rev_id}/complete", json={"metadata_json": '{"notes":"done"}'})
    assert res_comp.status_code == 200
    assert res_comp.json()["status"] == "COMPLETED"
    assert res_comp.json()["completed_at"] is not None

    # 7. Check no longer due
    res_due_after = test_client.get("/api/v1/reviews/due")
    assert not any(r["id"] == rev_id for r in res_due_after.json())

    # 8. Skip review (new review)
    res_rev2 = test_client.post(
        "/api/v1/reviews", json={"entity_id": cap_id, "entity_type": "Capture", "due_at": due_at}
    )
    rev_id2 = res_rev2.json()["id"]
    res_skip = test_client.post(f"/api/v1/reviews/{rev_id2}/skip")
    assert res_skip.status_code == 200
    assert res_skip.json()["status"] == "SKIPPED"

    # 9. Delete
    res_del = test_client.delete(f"/api/v1/reviews/{rev_id}")
    assert res_del.status_code == 204
