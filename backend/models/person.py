import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.orm import relationship as orm_relationship

from database import Base


def new_id():
    return str(uuid.uuid4())


class Person(Base):
    """
    A person the user has met and wants to remember.

    Kept deliberately small for MVP (Phase 1). This is the "stable profile" —
    fields that rarely change. Dynamic/changing facts (current city, current
    project, etc.) are NOT stored here; those live in the Memory table so
    they can be versioned over time (see Phase 12 in the plan: Bangalore ->
    Hyderabad should be a history, not an overwrite).
    """

    __tablename__ = "people"

    person_id = Column(String, primary_key=True, default=new_id)

    name = Column(String, nullable=False)
    relationship_label = Column(String, nullable=True)   # e.g. "College Friend"
    where_met = Column(String, nullable=True)             # e.g. "MES College"

    # Consent gate — recognition/recording must not run on a person
    # until this is explicitly true. See Section 18 (Privacy Principles).
    consented = Column(String, default="false", nullable=False)  # "true"/"false"

    relationship_strength = Column(Float, default=0.0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)

    # relationships to other tables
    faces = orm_relationship("Face", back_populates="person", cascade="all, delete-orphan")
    conversations = orm_relationship("Conversation", back_populates="person", cascade="all, delete-orphan")
    memories = orm_relationship("Memory", back_populates="person", cascade="all, delete-orphan")
    events = orm_relationship("Event", back_populates="person", cascade="all, delete-orphan")
    reminders = orm_relationship("Reminder", back_populates="person", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Person {self.name} ({self.person_id[:8]})>"
