import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship as orm_relationship

from database import Base


def new_id():
    return str(uuid.uuid4())


class Event(Base):
    """
    A dated life event on a person's timeline (Section 4.D / Phase 12).
    Distinct from Memory: an Event is a point on a timeline with a date
    ("Moved to Bangalore, 2024"), whereas a Memory is a current fact that
    may or may not have a specific date attached.
    """

    __tablename__ = "events"

    event_id = Column(String, primary_key=True, default=new_id)
    person_id = Column(String, ForeignKey("people.person_id"), nullable=False)

    event_type = Column(String, nullable=False)   # e.g. "new_job", "moved", "graduated"
    description = Column(Text, nullable=False)
    date = Column(DateTime, nullable=True)

    confidence = Column(Float, default=0.5, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    person = orm_relationship("Person", back_populates="events")

    def __repr__(self):
        return f"<Event {self.event_type} '{self.description[:40]}'>"
