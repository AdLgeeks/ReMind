import json
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship as orm_relationship

from database import Base


def new_id():
    return str(uuid.uuid4())


class Face(Base):
    """
    A single face embedding sample for a person.

    We store MULTIPLE Face rows per person (Phase 4: capture 5-10 images
    at different angles/lighting) rather than one embedding per person,
    so recognition can average or best-match across samples.

    Embedding is stored as a JSON-encoded list of floats in a Text column.
    This is fine for SQLite + a few hundred people. If this becomes a
    bottleneck, swap to FAISS for the similarity search itself while
    keeping this table as the source of truth.
    """

    __tablename__ = "faces"

    face_id = Column(String, primary_key=True, default=new_id)
    person_id = Column(String, ForeignKey("people.person_id"), nullable=False)

    embedding_json = Column(Text, nullable=False)  # JSON list of floats
    embedding_dim = Column(String, nullable=False)  # e.g. "512"
    det_score = Column(Float, nullable=True)  # detector confidence for this sample, 0-1

    created_at = Column(DateTime, default=datetime.utcnow)

    person = orm_relationship("Person", back_populates="faces")

    # --- helpers -----------------------------------------------------
    def set_embedding(self, vector: list[float]):
        self.embedding_json = json.dumps(vector)
        self.embedding_dim = str(len(vector))

    def get_embedding(self) -> list[float]:
        return json.loads(self.embedding_json)

    def __repr__(self):
        return f"<Face person={self.person_id[:8]} dim={self.embedding_dim}>"
