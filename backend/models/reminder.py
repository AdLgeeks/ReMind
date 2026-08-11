import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship as orm_relationship

from database import Base


def new_id():
    return str(uuid.uuid4())


class Reminder(Base):
    """
    An AI-generated contextual reminder (Section 4.H / Phase 13).
    e.g. "Ask John how his startup launch went."
    Not built in Phase 1 - table just needs to exist so later phases
    have somewhere to write to.
    """

    __tablename__ = "reminders"

    reminder_id = Column(String, primary_key=True, default=new_id)
    person_id = Column(String, ForeignKey("people.person_id"), nullable=False)

    reminder_text = Column(Text, nullable=False)
    priority = Column(String, default="normal")  # low | normal | high
    trigger_condition = Column(String, nullable=True)  # e.g. "next_interaction"
    status = Column(String, default="pending")  # pending | shown | dismissed | done

    created_at = Column(DateTime, default=datetime.utcnow)

    person = orm_relationship("Person", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder '{self.reminder_text[:40]}' status={self.status}>"
