import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship as orm_relationship

from database import Base


def new_id():
    return str(uuid.uuid4())


class Conversation(Base):
    """
    A single recorded conversation/event with a person.
    This is the "episodic memory" — raw source of truth.

    Memory rows (facts) are extracted FROM a conversation and keep a
    source_conversation_id pointing back here, so every fact is traceable
    to the moment it was said.
    """

    __tablename__ = "conversations"

    conversation_id = Column(String, primary_key=True, default=new_id)
    person_id = Column(String, ForeignKey("people.person_id"), nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(String, nullable=True)

    transcript = Column(Text, nullable=True)  # raw speech-to-text output
    summary = Column(Text, nullable=True)     # LLM-generated summary

    person = orm_relationship("Person", back_populates="conversations")
    memories = orm_relationship("Memory", back_populates="source_conversation")

    def __repr__(self):
        return f"<Conversation person={self.person_id[:8]} at={self.timestamp}>"
