import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship as orm_relationship

from database import Base


def new_id():
    return str(uuid.uuid4())


class MemoryType(str, enum.Enum):
    PROFILE = "PROFILE"
    INTEREST = "INTEREST"
    LIFE_EVENT = "LIFE_EVENT"
    PROJECT = "PROJECT"
    RELATIONSHIP = "RELATIONSHIP"
    TASK = "TASK"
    DECISION = "DECISION"
    COMMITMENT = "COMMITMENT"
    PREFERENCE = "PREFERENCE"
    GENERAL = "GENERAL"


class Memory(Base):
    """
    A single structured fact about a person (Section 6 & 12 of the plan).

    Versioning / contradiction handling:
    When a new fact contradicts an existing one for the same
    (person_id, type, predicate), Phase 1 does NOT decide the merge logic
    (that's Phase 8/9 - memory extraction service). This table just needs
    to be ABLE to represent a history chain, via valid_from/valid_until
    and superseded_by_id.

    Example (Bangalore -> Hyderabad):
      Memory A: fact="Lives in Bangalore", valid_from=T1, valid_until=T2,
                superseded_by_id=Memory B.memory_id
      Memory B: fact="Lives in Hyderabad", valid_from=T2, valid_until=None
    """

    __tablename__ = "memories"

    memory_id = Column(String, primary_key=True, default=new_id)
    person_id = Column(String, ForeignKey("people.person_id"), nullable=False)
    source_conversation_id = Column(String, ForeignKey("conversations.conversation_id"), nullable=True)

    type = Column(SAEnum(MemoryType), nullable=False, default=MemoryType.GENERAL)
    predicate = Column(String, nullable=True)   # e.g. "lives_in", "interested_in"
    fact = Column(Text, nullable=False)          # human-readable fact text

    importance = Column(Float, default=0.5, nullable=False)   # 0-1
    confidence = Column(Float, default=0.5, nullable=False)   # 0-1

    mention_count = Column(Float, default=1)  # int, but keeps things simple with default

    created_at = Column(DateTime, default=datetime.utcnow)
    last_confirmed = Column(DateTime, default=datetime.utcnow)

    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)  # null = currently valid
    superseded_by_id = Column(String, ForeignKey("memories.memory_id"), nullable=True)

    source = Column(String, default="conversation")  # conversation | manual | inferred

    person = orm_relationship("Person", back_populates="memories")
    source_conversation = orm_relationship("Conversation", back_populates="memories")

    def __repr__(self):
        return f"<Memory {self.type} '{self.fact[:40]}' person={self.person_id[:8]}>"
