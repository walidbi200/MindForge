"""Integration tests for /api/v1/reviews endpoints."""

from uuid import uuid4

import pytest


def create_capture(test_client) -> str:
    """Helper: create a capture and return its ID."""
    resp = test_client.post(
        "/api/v1/captures",
        json={"content": "Test capture content for review testing"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


class TestCreateReview:
    def test_create_review(self, test_client):
        capture_id = create_capture(test_client)
        resp = test_client.post(
            "/api/v1/reviews",
            json={
                "entity_id": capture_id,
                "entity_type": "Capture",
                "review_type": "RECALL",
                "difficulty": "MEDIUM",
                "notes": "Test review",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["entity_id"] == capture_id
        assert data["entity_type"] == "Capture"
        assert data["review_type"] == "RECALL"
        assert data["status"] == "NEW"
        assert data["notes"] == "Test review"

    def test_create_duplicate_raises_400(self, test_client):
        capture_id = create_capture(test_client)
        payload = {
            "entity_id": capture_id,
            "entity_type": "Capture",
            "review_type": "READ",
            "difficulty": "EASY",
            "notes": "",
        }
        resp1 = test_client.post("/api/v1/reviews", json=payload)
        assert resp1.status_code == 201

        resp2 = test_client.post("/api/v1/reviews", json=payload)
        assert resp2.status_code == 400
        assert "already exists" in resp2.json()["error"]["message"]

    def test_create_review_unknown_entity_400(self, test_client):
        resp = test_client.post(
            "/api/v1/reviews",
            json={
                "entity_id": str(uuid4()),
                "entity_type": "Capture",
                "review_type": "QUIZ",
                "difficulty": "HARD",
                "notes": "",
            },
        )
        assert resp.status_code == 400
        assert "does not exist" in resp.json()["error"]["message"]


class TestGetReview:
    def test_get_existing(self, test_client):
        capture_id = create_capture(test_client)
        create_resp = test_client.post(
            "/api/v1/reviews",
            json={
                "entity_id": capture_id,
                "entity_type": "Capture",
                "review_type": "FLASHCARD",
                "difficulty": "MEDIUM",
                "notes": "",
            },
        )
        review_id = create_resp.json()["id"]

        resp = test_client.get(f"/api/v1/reviews/{review_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == review_id

    def test_get_missing_404(self, test_client):
        resp = test_client.get(f"/api/v1/reviews/{uuid4()}")
        assert resp.status_code == 404


class TestListReviews:
    def test_list_returns_ok(self, test_client):
        resp = test_client.get("/api/v1/reviews")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_due_returns_ok(self, test_client):
        resp = test_client.get("/api/v1/reviews/due")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestCompleteReview:
    def test_complete_review(self, test_client):
        capture_id = create_capture(test_client)
        create_resp = test_client.post(
            "/api/v1/reviews",
            json={
                "entity_id": capture_id,
                "entity_type": "Capture",
                "review_type": "RECALL",
                "difficulty": "MEDIUM",
                "notes": "",
            },
        )
        assert create_resp.status_code == 201
        review_id = create_resp.json()["id"]

        complete_resp = test_client.post(
            f"/api/v1/reviews/{review_id}/complete",
            json={"difficulty": "EASY", "score": 4, "notes": "Recalled well"},
        )
        assert complete_resp.status_code == 200
        data = complete_resp.json()
        assert data["score"] == 4
        assert data["difficulty"] == "EASY"
        assert data["notes"] == "Recalled well"
        assert data["last_reviewed_at"] is not None
        assert data["next_review_at"] is not None
        assert data["status"] == "REVIEWING"

    def test_complete_missing_review_404(self, test_client):
        resp = test_client.post(
            f"/api/v1/reviews/{uuid4()}/complete",
            json={"difficulty": "MEDIUM", "score": 3, "notes": ""},
        )
        assert resp.status_code == 404


class TestDeleteReview:
    def test_delete_review(self, test_client):
        capture_id = create_capture(test_client)
        create_resp = test_client.post(
            "/api/v1/reviews",
            json={
                "entity_id": capture_id,
                "entity_type": "Capture",
                "review_type": "QUIZ",
                "difficulty": "MEDIUM",
                "notes": "",
            },
        )
        review_id = create_resp.json()["id"]

        del_resp = test_client.delete(f"/api/v1/reviews/{review_id}")
        assert del_resp.status_code == 204

        get_resp = test_client.get(f"/api/v1/reviews/{review_id}")
        assert get_resp.status_code == 404

    def test_delete_missing_404(self, test_client):
        resp = test_client.delete(f"/api/v1/reviews/{uuid4()}")
        assert resp.status_code == 404
