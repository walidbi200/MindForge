def test_timeline_records_events(test_client):
    # 1. POST Capture
    res_cap = test_client.post("/api/v1/captures", json={"content": "timeline capture"})
    assert res_cap.status_code == 201
    cap_id = res_cap.json()["id"]

    # 2. POST Concept
    res_con = test_client.post("/api/v1/concepts", json={"title": "T", "summary": "S"})
    assert res_con.status_code == 201
    con_id = res_con.json()["id"]

    # 3. GET Timeline
    res_timeline = test_client.get("/api/v1/timeline")
    assert res_timeline.status_code == 200
    events = res_timeline.json()

    # The latest event is first
    assert events[0]["event_type"] == "ConceptCreated"
    assert events[0]["aggregate_id"] == con_id
    assert events[1]["event_type"] == "CaptureCreated"
    assert events[1]["aggregate_id"] == cap_id

    # 4. Rollback validation (implicitly verified by next test if UoW doesn't commit)
