def test_source_api_lifecycle(test_client):
    # 1. Create Source
    res = test_client.post(
        "/api/v1/sources",
        json={
            "title": "Article Title",
            "source_type": "WEB_ARTICLE",
            "uri": "https://example.com/api-test",
            "author": "Test Author",
        },
    )
    assert res.status_code == 201
    data = res.json()
    sid = data["id"]
    assert data["title"] == "Article Title"
    assert data["source_type"] == "WEB_ARTICLE"
    assert data["uri"] == "https://example.com/api-test"
    assert data["author"] == "Test Author"

    # 2. Get Source
    res = test_client.get(f"/api/v1/sources/{sid}")
    assert res.status_code == 200
    assert res.json()["title"] == "Article Title"

    # 3. Update Source
    res = test_client.patch(
        f"/api/v1/sources/{sid}",
        json={"title": "Updated Title", "language": "es"},
    )
    assert res.status_code == 200
    assert res.json()["title"] == "Updated Title"
    assert res.json()["language"] == "es"

    # 4. List Sources
    res = test_client.get("/api/v1/sources?limit=10")
    assert res.status_code == 200
    sources = res.json()
    assert len(sources) >= 1
    assert any(s["id"] == sid for s in sources)

    # List with filtering
    res = test_client.get("/api/v1/sources?source_type=BOOK")
    assert res.status_code == 200
    assert len(res.json()) == 0

    # 5. Delete Source
    res = test_client.delete(f"/api/v1/sources/{sid}")
    assert res.status_code == 204

    # Verify 404 on get
    res = test_client.get(f"/api/v1/sources/{sid}")
    assert res.status_code == 404
