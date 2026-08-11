from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

# check_same_thread=False is needed because FastAPI can use the
# session from a different thread than the one that created it.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables that don't exist yet. Safe to call repeatedly."""
    # Import models here so they register on Base.metadata before create_all.
    from models import person, face, conversation, memory, event, relationship, reminder  # noqa: F401

    Base.metadata.create_all(bind=engine)
