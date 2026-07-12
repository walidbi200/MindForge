#!/usr/bin/env python3
"""
MindForge Production Smoke Test
================================
Runs a scripted end-to-end workflow against the live production URLs.

Usage:
    python scripts/smoke_test.py \
        --api-url https://your-app.up.railway.app \
        --app-key YOUR_APP_SECRET_KEY

Requirements:
    pip install httpx  (or: uv pip install httpx)
"""

import argparse
import json
import sys
from datetime import datetime, timezone

try:
    import httpx
except ImportError:
    print("ERROR: httpx is required. Install with: pip install httpx")
    sys.exit(1)


def run(api_url: str, app_key: str, timeout: int = 30) -> None:
    api_url = api_url.rstrip("/")
    headers = {"X-Ascend-Key": app_key}
    client = httpx.Client(timeout=timeout)

    print(f"\n🔍 Smoke testing: {api_url}\n")

    # --- Step 1: Health Check ---
    print("Step 1 — Health check")
    r = client.get(f"{api_url}/api/v1/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("status") == "ok", f"Unexpected health payload: {data}"
    print(f"  ✅ OK  (version={data.get('version', '?')})")

    # --- Step 2: Create a capture ---
    print("Step 2 — Create capture")
    payload = {
        "content": f"[smoke-test] {datetime.now(timezone.utc).isoformat()} — MindForge production smoke test."
    }
    r = client.post(f"{api_url}/api/v1/captures", json=payload)
    assert r.status_code == 201, f"Create capture failed: {r.status_code} {r.text}"
    capture = r.json()
    capture_id = capture["id"]
    print(f"  ✅ Created capture: {capture_id}")

    # --- Step 3: AI analysis ---
    print("Step 3 — AI analysis (uses OpenRouter)")
    r = client.post(
        f"{api_url}/api/v1/ai/analyze-capture/{capture_id}",
        headers=headers,
    )
    assert r.status_code == 200, f"AI analysis failed: {r.status_code} {r.text}"
    analysis = r.json()
    assert "concepts" in analysis, f"No concepts in AI response: {analysis}"
    print(f"  ✅ AI analysis OK — {len(analysis['concepts'])} concept(s) suggested")

    # --- Step 4: Confirm capture persists in DB ---
    print("Step 4 — Confirm persistence in database")
    r = client.get(f"{api_url}/api/v1/captures/{capture_id}")
    assert r.status_code == 200, f"Fetch capture failed: {r.status_code} {r.text}"
    fetched = r.json()
    assert fetched["id"] == capture_id, "Capture ID mismatch"
    print(f"  ✅ Capture persists: {fetched['id']}")

    # --- Step 5: Create and load a review session ---
    print("Step 5 — Create and load a review session")
    due_at = datetime.now(timezone.utc).isoformat()
    r = client.post(
        f"{api_url}/api/v1/reviews",
        json={
            "entity_id": capture_id,
            "entity_type": "Capture",
            "due_at": due_at,
            "metadata_json": "{}",
        },
    )
    assert r.status_code == 201, f"Create review failed: {r.status_code} {r.text}"
    review = r.json()
    review_id = review["id"]

    r = client.get(f"{api_url}/api/v1/reviews/due")
    assert r.status_code == 200, f"List due reviews failed: {r.status_code} {r.text}"
    due_ids = [rev["id"] for rev in r.json()]
    assert review_id in due_ids, f"Review {review_id} not in due list: {due_ids}"
    print(f"  ✅ Review session loaded: {review_id}")

    # --- Step 6: Verify protected endpoint rejects requests without key ---
    print("Step 6 — Verify endpoint protection (expect 403 without key)")
    r = client.post(
        f"{api_url}/api/v1/ai/analyze-capture/{capture_id}",
        # No X-Ascend-Key header
    )
    if app_key:
        # Only meaningful to test when APP_SECRET_KEY is set on the server
        assert r.status_code == 403, f"Expected 403 without key, got: {r.status_code}"
        print("  ✅ 403 returned correctly for unauthenticated AI request")
    else:
        print("  ⚠️  Skipped (no APP_SECRET_KEY set on server — protection is off)")

    print("\n🎉 All smoke tests passed!\n")
    client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="MindForge production smoke test")
    parser.add_argument("--api-url", required=True, help="Railway API base URL")
    parser.add_argument("--app-key", default="", help="X-Ascend-Key shared secret")
    args = parser.parse_args()

    try:
        run(args.api_url, args.app_key)
    except AssertionError as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}\n")
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"\n❌ NETWORK ERROR: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
