from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.person import Person
from schemas.person import PersonCreate, PersonUpdate, PersonOut

router = APIRouter(prefix="/people", tags=["people"])


@router.post("", response_model=PersonOut, status_code=201)
def create_person(payload: PersonCreate, db: Session = Depends(get_db)):
    """Register a new person (Section 3, step 1)."""
    person = Person(
        name=payload.name,
        relationship_label=payload.relationship_label,
        where_met=payload.where_met,
        consented="true" if payload.consented else "false",
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return PersonOut.from_orm_person(person)


@router.get("", response_model=list[PersonOut])
def list_people(db: Session = Depends(get_db)):
    """List everyone registered so far."""
    people = db.query(Person).order_by(Person.created_at.desc()).all()
    return [PersonOut.from_orm_person(p) for p in people]


@router.get("/{person_id}", response_model=PersonOut)
def get_person(person_id: str, db: Session = Depends(get_db)):
    """Fetch a single person's stable profile."""
    person = db.query(Person).filter_by(person_id=person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return PersonOut.from_orm_person(person)


@router.patch("/{person_id}", response_model=PersonOut)
def update_person(person_id: str, payload: PersonUpdate, db: Session = Depends(get_db)):
    """Partial update - e.g. correcting a name, or granting/revoking consent."""
    person = db.query(Person).filter_by(person_id=person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    if payload.name is not None:
        person.name = payload.name
    if payload.relationship_label is not None:
        person.relationship_label = payload.relationship_label
    if payload.where_met is not None:
        person.where_met = payload.where_met
    if payload.consented is not None:
        person.consented = "true" if payload.consented else "false"

    db.commit()
    db.refresh(person)
    return PersonOut.from_orm_person(person)


@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: str, db: Session = Depends(get_db)):
    """
    'Forget this person' (Section 18, privacy requirement #7).
    Cascade delete is configured on the Person model relationships
    (faces, conversations, memories, events, reminders all get removed
    with it) - so this is a genuine full erase, not just hiding a row.
    """
    person = db.query(Person).filter_by(person_id=person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()
    return None


@router.post("/{person_id}/mark-seen", response_model=PersonOut)
def mark_seen(person_id: str, db: Session = Depends(get_db)):
    """
    Bump last_seen to now. Called whenever recognition successfully
    matches this person (used by Phase 4/11 recognition flow later) -
    kept here now since it's simple, person-scoped state.
    """
    person = db.query(Person).filter_by(person_id=person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    person.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(person)
    return PersonOut.from_orm_person(person)
