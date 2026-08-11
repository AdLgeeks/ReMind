from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models.person import Person
from models.face import Face
from schemas.face import FaceOut, FaceCaptureSummary
from services.face_service import (
    extract_single_face_embedding,
    NoFaceDetectedError,
    MultipleFacesDetectedError,
)

router = APIRouter(prefix="/people", tags=["faces"])

# Enrollment quality bar - matches Section 4 plan of "5-10 images, different
# angles/lighting" for robust recognition later (Phase 4).
RECOMMENDED_SAMPLE_COUNT = 5


@router.post("/{person_id}/faces", response_model=FaceCaptureSummary, status_code=201)
async def capture_face(
    person_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Register a face sample photo for a person (Phase 3, Section 3 steps 2-4).

    Consent gate: this is a hard block, not a warning. A person must have
    consented=true before any biometric data is captured for them
    (Section 18, privacy principle #1-2).

    Note: we do NOT store the uploaded image itself, only the derived
    embedding vector - Section 18 privacy principle #4: "No unnecessary
    raw image storage."
    """
    person = db.query(Person).filter_by(person_id=person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if person.consented != "true":
        raise HTTPException(
            status_code=403,
            detail="This person has not consented. Cannot capture biometric data.",
        )

    image_bytes = await file.read()

    try:
        embedding, det_score, bbox = extract_single_face_embedding(image_bytes)
    except NoFaceDetectedError:
        raise HTTPException(status_code=422, detail="No face detected in image. Please retake the photo.")
    except MultipleFacesDetectedError as e:
        raise HTTPException(
            status_code=422,
            detail=f"{e.count} faces detected. Please capture one person at a time.",
        )

    face = Face(person_id=person_id, det_score=det_score)
    face.set_embedding(embedding)
    db.add(face)
    db.commit()
    db.refresh(face)

    total = db.query(Face).filter_by(person_id=person_id).count()

    return FaceCaptureSummary(
        face=FaceOut.model_validate(face),
        total_samples_for_person=total,
    )


@router.get("/{person_id}/faces", response_model=list[FaceOut])
def list_faces(person_id: str, db: Session = Depends(get_db)):
    """List face samples captured for a person (metadata only, no raw images)."""
    person = db.query(Person).filter_by(person_id=person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    faces = db.query(Face).filter_by(person_id=person_id).all()
    return [FaceOut.model_validate(f) for f in faces]


@router.delete("/{person_id}/faces/{face_id}", status_code=204)
def delete_face(person_id: str, face_id: str, db: Session = Depends(get_db)):
    """Remove a single bad sample (e.g. blurry capture) without deleting the whole person."""
    face = db.query(Face).filter_by(face_id=face_id, person_id=person_id).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face sample not found")
    db.delete(face)
    db.commit()
    return None
