import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship as orm_relationship

from database import Base


def new_id():
    return str(uuid.uuid4())


class RelationshipMilestone(Base):
    """
    Tracks how the RELATIONSHIP itself evolves over time
    (Section 4.F): First meeting -> Friend -> Worked together ->
    Lost contact -> Reconnected -> Business partner.

    This is intentionally separate from Event (which tracks the
    PERSON's life events like a new job or moving cities). A
    RelationshipMilestone is specifically about the user's connection
    to that person changing state.
    """

    __tablename__ = "relationship_milestones"

    milestone_id = Column(String, primary_key=True, default=new_id)
    person_id = Column(String, ForeignKey("people.person_id"), nullable=False)

    label = Column(String, nullable=False)   # e.g. "Friend", "Business Partner", "Reconnected"
    note = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    person = orm_relationship("Person")

    def __repr__(self):
        return f"<RelationshipMilestone {self.label} person={self.person_id[:8]}>"
