from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PersonCreate(BaseModel):
    """What the client sends to register a new person (Section 3, steps 1-4)."""
    name: str = Field(..., min_length=1, max_length=200)
    relationship_label: Optional[str] = Field(None, max_length=100)
    where_met: Optional[str] = Field(None, max_length=200)

    # Consent must be explicit. Default False on purpose - the client has
    # to deliberately set this true. No face capture or recording should
    # be allowed (Phase 3+) until this is true. See Section 18.
    consented: bool = False


class PersonUpdate(BaseModel):
    """Partial update - all fields optional. Used e.g. when relationship
    label changes or consent is granted/revoked after the fact."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    relationship_label: Optional[str] = None
    where_met: Optional[str] = None
    consented: Optional[bool] = None


class PersonOut(BaseModel):
    """What the API returns for a person."""
    model_config = ConfigDict(from_attributes=True)

    person_id: str
    name: str
    relationship_label: Optional[str] = None
    where_met: Optional[str] = None
    consented: bool
    relationship_strength: float
    created_at: datetime
    last_seen: Optional[datetime] = None

    @classmethod
    def from_orm_person(cls, person):
        """Person.consented is stored as string "true"/"false" in the DB
        (see models/person.py) - convert it to a real bool for the API."""
        return cls(
            person_id=person.person_id,
            name=person.name,
            relationship_label=person.relationship_label,
            where_met=person.where_met,
            consented=(person.consented == "true"),
            relationship_strength=person.relationship_strength,
            created_at=person.created_at,
            last_seen=person.last_seen,
        )
