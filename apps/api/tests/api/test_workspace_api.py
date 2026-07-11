def test_get_workspace_summary(test_client):
    response = test_client.get("/api/v1/workspace")
    assert response.status_code == 200
    data = response.json()
    assert "due_reviews" in data
    assert "recent_captures" in data
    assert "pinned_spaces" in data
    assert "recent_sources" in data
    assert "activity" in data
    assert "graph_preview" in data
    assert "recent_concepts" in data
    assert "recent_collections" in data
    assert "pending_proposals" in data
    assert "continue_learning" in data
    assert "daily_stats" in data
    
    stats = data["daily_stats"]
    assert "captures_today" in stats
    assert "reviews_completed_today" in stats
    assert "concepts_today" in stats
    assert "pending_proposals" in stats
    assert "goal_progress" in stats


def test_search_workspace(test_client):
    # Search for something that doesn't exist
    response = test_client.get("/api/v1/workspace/search?q=missing")
    assert response.status_code == 200
    assert response.json() == []

    # Create a capture
    test_client.post("/api/v1/captures", json={"content": "Search me"})

    # Search for the capture
    response = test_client.get("/api/v1/workspace/search?q=Search")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["type"] == "Capture"
    assert "Search me" in data[0]["snippet"]
