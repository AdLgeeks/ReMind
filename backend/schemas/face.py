from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FaceOut(BaseModel):
    """
    What the API returns after a successful face capture.
    Deliberately does NOT include the raw embedding vector in the
    response - the client doesn't need it, and there's no reason to
    send 512 floats over the wire to a phone that's just showing
    "Sample 3 of 5 captured".
    """
    model_config = ConfigDict(from_attributes=True)

    face_id: str
    person_id: str
    embedding_dim: str
    det_score: float
    created_at: datetime


class FaceCaptureSummary(BaseModel):
    """Returned after each capture - tells the client how many good
    samples exist so far, so the UI can show "3 of 5 captured"."""
    face: FaceOut
    total_samples_for_person: int
