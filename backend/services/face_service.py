"""
Face detection + embedding generation (Phase 3).

Scope of this file, on purpose:
- detect faces in an image
- reject images that don't have exactly one clear face (enrollment needs
  one unambiguous face per sample - see Section 8: "never force an identity")
- return a 512-dim embedding vector for that face

What this file does NOT do (that's Phase 4):
- compare an embedding against the database to identify a person
- decide a similarity threshold

Model: InsightFace 'buffalo_sc' (small/fast variant of buffalo_l - good
enough for a phone-camera MVP and much faster to load). Swappable later
for a larger model by changing MODEL_NAME below if accuracy needs it.
"""
import io
import threading

import cv2
import numpy as np
from insightface.app import FaceAnalysis

MODEL_NAME = "buffalo_sc"
DET_SIZE = (320, 320)

_app = None
_app_lock = threading.Lock()


class NoFaceDetectedError(Exception):
    pass


class MultipleFacesDetectedError(Exception):
    def __init__(self, count: int):
        self.count = count
        super().__init__(f"{count} faces detected, expected exactly 1")


def _get_app() -> FaceAnalysis:
    """
    Lazily load the model once per process and reuse it.
    Loading takes real time (model weights + ONNX runtime init), so we do
    NOT want to reload it on every request.
    """
    global _app
    if _app is None:
        with _app_lock:
            if _app is None:  # double-checked locking
                app = FaceAnalysis(name=MODEL_NAME, providers=["CPUExecutionProvider"])
                app.prepare(ctx_id=0, det_size=DET_SIZE)
                _app = app
    return _app


def extract_single_face_embedding(image_bytes: bytes) -> tuple[list[float], float, list[float]]:
    """
    Given raw image bytes (e.g. from an uploaded JPEG/PNG), detect faces
    and return the embedding for exactly one face.

    Returns: (embedding, det_score, bbox)
      - embedding: list[float], length 512
      - det_score: float, detector's confidence this is a face (0-1)
      - bbox: [x1, y1, x2, y2]

    Raises:
      - NoFaceDetectedError if zero faces found
      - MultipleFacesDetectedError if more than one face found
        (enrollment should show exactly one person - ask the user to
        retake the photo rather than guessing which face is the target)
    """
    np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise NoFaceDetectedError()

    app = _get_app()
    faces = app.get(img)

    if len(faces) == 0:
        raise NoFaceDetectedError()
    if len(faces) > 1:
        raise MultipleFacesDetectedError(len(faces))

    face = faces[0]
    embedding = face.embedding.astype(float).tolist()
    det_score = float(face.det_score)
    bbox = [float(x) for x in face.bbox]
    return embedding, det_score, bbox
