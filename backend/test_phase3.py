"""
Phase 3 test script.

Tests real face detection + embedding generation through the actual API,
using a real downloaded test image (not a mock) so this proves the whole
pipeline - upload -> detect -> embed -> store -> retrieve.

Usage:
    cd backend
    python test_phase3.py

Requires: /tmp/test_face.jpg (a real photo with exactly one face) and
/tmp/no_face.jpg (an image with no face) to already exist. The script
will create them if missing (downloads a public-domain test photo).
"""
import io
import os
import subprocess

import numpy as np
import cv2
from fastapi.testclient import TestClient

from database import init_db
from main import app

client = TestClient(app)

TEST_FACE_PATH = "/tmp/test_face.jpg"
NO_FACE_PATH = "/tmp/no_face.jpg"


def ensure_test_images():
    if not os.path.exists(TEST_FACE_PATH):
        subprocess.run([
            "curl", "-sL", "-o", TEST_FACE_PATH,
            "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg",
        ], check=True)
    if not os.path.exists(NO_FACE_PATH):
        # A flat gray image - no face in it.
        blank = np.full((300, 300, 3), 128, dtype=np.uint8)
        cv2.imwrite(NO_FACE_PATH, blank)


def main():
    ensure_test_images()
    init_db()

    # 1. Register John WITHOUT consent first, to prove the consent gate works
    resp = client.post("/people", json={"name": "John", "relationship_label": "College Friend"})
    john_id = resp.json()["person_id"]

    with open(TEST_FACE_PATH, "rb") as f:
        resp = client.post(f"/people/{john_id}/faces", files={"file": ("face.jpg", f, "image/jpeg")})
    assert resp.status_code == 403, resp.text
    print("OK: face capture blocked for non-consented person (403)")

    # 2. Grant consent, retry
    client.patch(f"/people/{john_id}", json={"consented": True})
    with open(TEST_FACE_PATH, "rb") as f:
        resp = client.post(f"/people/{john_id}/faces", files={"file": ("face.jpg", f, "image/jpeg")})
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["face"]["embedding_dim"] == "512"
    assert body["total_samples_for_person"] == 1
    print(f"OK: captured real face embedding -> det_score={body['face']['det_score']:.3f}, "
          f"dim={body['face']['embedding_dim']}")

    # 3. Capture a second sample of the same photo - simulates "capture 5-10 images"
    with open(TEST_FACE_PATH, "rb") as f:
        resp = client.post(f"/people/{john_id}/faces", files={"file": ("face2.jpg", f, "image/jpeg")})
    assert resp.status_code == 201
    assert resp.json()["total_samples_for_person"] == 2
    print("OK: second sample captured, total_samples_for_person=2")

    # 4. Upload an image with NO face -> should be rejected with 422
    with open(NO_FACE_PATH, "rb") as f:
        resp = client.post(f"/people/{john_id}/faces", files={"file": ("blank.jpg", f, "image/jpeg")})
    assert resp.status_code == 422, resp.text
    print(f"OK: no-face image rejected -> {resp.json()['detail']}")

    # 5. List faces for John
    resp = client.get(f"/people/{john_id}/faces")
    assert resp.status_code == 200
    faces = resp.json()
    assert len(faces) == 2
    print(f"OK: listed {len(faces)} face samples for John")

    # 6. Delete one bad sample
    face_id_to_delete = faces[0]["face_id"]
    resp = client.delete(f"/people/{john_id}/faces/{face_id_to_delete}")
    assert resp.status_code == 204
    resp = client.get(f"/people/{john_id}/faces")
    assert len(resp.json()) == 1
    print("OK: deleted one face sample, 1 remaining")

    # 7. 404 for capturing a face on a nonexistent person
    with open(TEST_FACE_PATH, "rb") as f:
        resp = client.post("/people/does-not-exist/faces", files={"file": ("face.jpg", f, "image/jpeg")})
    assert resp.status_code == 404
    print("OK: 404 for unknown person_id on face capture")

    print("\nAll Phase 3 checks passed (using a real face detection model, not a mock).")


if __name__ == "__main__":
    main()
