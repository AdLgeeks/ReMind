"""
Phase 2 test script.

Tests the Person Registration API (create, list, get, update, mark-seen,
delete) by driving it exactly the way a mobile client would - real HTTP
calls against the FastAPI app, no shortcuts through the DB directly.

Usage:
    cd backend
    python test_phase2.py

Expected: a series of "OK" lines, no tracebacks.
"""
from fastapi.testclient import TestClient

from database import init_db
from main import app

client = TestClient(app)


def main():
    init_db()

    # 1. Register a person WITHOUT consent (default False)
    resp = client.post("/people", json={
        "name": "Sarah",
        "relationship_label": "Coworker",
        "where_met": "Google offices",
    })
    assert resp.status_code == 201, resp.text
    sarah = resp.json()
    assert sarah["consented"] is False
    print(f"OK: created Sarah without consent -> {sarah['person_id']}")

    # 2. Register a person WITH consent (John, matching the MVP demo)
    resp = client.post("/people", json={
        "name": "John",
        "relationship_label": "College Friend",
        "where_met": "MES College",
        "consented": True,
    })
    assert resp.status_code == 201, resp.text
    john = resp.json()
    assert john["consented"] is True
    john_id = john["person_id"]
    print(f"OK: created John with consent -> {john_id}")

    # 3. List people - both should be present
    resp = client.get("/people")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "Sarah" in names and "John" in names
    print(f"OK: listed people -> {names}")

    # 4. Get a single person
    resp = client.get(f"/people/{john_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "John"
    print("OK: fetched John by id")

    # 5. Get a person that doesn't exist -> 404
    resp = client.get("/people/does-not-exist")
    assert resp.status_code == 404
    print("OK: 404 for unknown person_id")

    # 6. Update John's relationship label
    resp = client.patch(f"/people/{john_id}", json={"relationship_label": "Business Partner"})
    assert resp.status_code == 200
    assert resp.json()["relationship_label"] == "Business Partner"
    print("OK: updated John's relationship_label")

    # 7. Revoke Sarah's consent explicitly (should already be False, but test the flip)
    resp = client.post("/people", json={"name": "TempConsentTest", "consented": True})
    temp_id = resp.json()["person_id"]
    resp = client.patch(f"/people/{temp_id}", json={"consented": False})
    assert resp.status_code == 200
    assert resp.json()["consented"] is False
    print("OK: consent can be revoked via PATCH")

    # 8. mark-seen bumps last_seen from null to a timestamp
    resp = client.get(f"/people/{john_id}")
    assert resp.json()["last_seen"] is None
    resp = client.post(f"/people/{john_id}/mark-seen")
    assert resp.status_code == 200
    assert resp.json()["last_seen"] is not None
    print("OK: mark-seen sets last_seen")

    # 9. Delete ("forget") a person, then confirm it's gone
    resp = client.delete(f"/people/{temp_id}")
    assert resp.status_code == 204
    resp = client.get(f"/people/{temp_id}")
    assert resp.status_code == 404
    print("OK: delete (forget person) removes the record")

    print("\nAll Phase 2 checks passed.")


if __name__ == "__main__":
    main()
