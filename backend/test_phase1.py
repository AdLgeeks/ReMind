"""
Phase 1 test script.

Run this to prove the data models work before building anything on top
of them (camera, Whisper, LLM extraction, etc).

Usage:
    cd backend
    python test_phase1.py

Expected: prints a series of "OK" lines and a final memory summary
for a fake person "John", with no errors/tracebacks.
"""
from datetime import datetime

from database import init_db, SessionLocal
from models.person import Person
from models.face import Face
from models.conversation import Conversation
from models.memory import Memory, MemoryType
from models.event import Event
from models.relationship import RelationshipMilestone
from models.reminder import Reminder


def main():
    init_db()
    db = SessionLocal()

    try:
        # 1. Register a person (consent required before any face/recording use)
        john = Person(
            name="John",
            relationship_label="College Friend",
            where_met="MES College",
            consented="true",
        )
        db.add(john)
        db.commit()
        db.refresh(john)
        print(f"OK: created person -> {john}")

        # 2. Add a fake face embedding (normally comes from InsightFace/ArcFace)
        face = Face(person_id=john.person_id)
        face.set_embedding([0.01 * i for i in range(512)])  # fake 512-dim vector
        db.add(face)
        db.commit()
        print(f"OK: created face -> {face}, dim={face.embedding_dim}, "
              f"round-trip length={len(face.get_embedding())}")

        # 3. Log a conversation (episodic memory / raw source of truth)
        convo = Conversation(
            person_id=john.person_id,
            timestamp=datetime.utcnow(),
            location="Coffee shop",
            transcript="John: I'm starting an AI startup focused on computer vision. "
                       "I'm also moving to Bangalore next month.",
            summary="John is starting a computer vision AI startup and moving to Bangalore.",
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)
        print(f"OK: created conversation -> {convo}")

        # 4. Extract structured memories from that conversation
        mem_project = Memory(
            person_id=john.person_id,
            source_conversation_id=convo.conversation_id,
            type=MemoryType.PROJECT,
            predicate="working_on",
            fact="Starting an AI startup",
            importance=0.95,
            confidence=0.9,
        )
        mem_interest = Memory(
            person_id=john.person_id,
            source_conversation_id=convo.conversation_id,
            type=MemoryType.INTEREST,
            predicate="interested_in",
            fact="Computer vision",
            importance=0.8,
            confidence=0.9,
        )
        mem_location = Memory(
            person_id=john.person_id,
            source_conversation_id=convo.conversation_id,
            type=MemoryType.LIFE_EVENT,
            predicate="lives_in",
            fact="Moving to Bangalore",
            importance=0.85,
            confidence=0.85,
        )
        db.add_all([mem_project, mem_interest, mem_location])
        db.commit()
        print(f"OK: created 3 memories")

        # 5. Log a life event on the timeline
        event = Event(
            person_id=john.person_id,
            event_type="moving",
            description="Moving to Bangalore",
            date=datetime.utcnow(),
            confidence=0.85,
        )
        db.add(event)
        db.commit()
        print(f"OK: created event -> {event}")

        # 6. Log a relationship milestone
        milestone = RelationshipMilestone(
            person_id=john.person_id,
            label="Friend",
            note="Reconnected after college",
        )
        db.add(milestone)
        db.commit()
        print(f"OK: created relationship milestone -> {milestone}")

        # 7. Create a reminder
        reminder = Reminder(
            person_id=john.person_id,
            reminder_text="Ask John how his startup launch went.",
            priority="high",
            trigger_condition="next_interaction",
        )
        db.add(reminder)
        db.commit()
        print(f"OK: created reminder -> {reminder}")

        # --- Simulate the MVP demo query: "point camera at John" -> retrieve memory ---
        print("\n--- Simulated retrieval for John ---")
        person = db.query(Person).filter_by(name="John").first()
        memories = db.query(Memory).filter_by(person_id=person.person_id).all()
        events = db.query(Event).filter_by(person_id=person.person_id).all()
        reminders = db.query(Reminder).filter_by(person_id=person.person_id).all()

        print(f"{person.name} - {person.relationship_label} - met at {person.where_met}")
        print("Memories:")
        for m in memories:
            print(f"  [{m.type.value}] {m.fact} (importance={m.importance}, confidence={m.confidence})")
        print("Life events:")
        for e in events:
            print(f"  {e.event_type}: {e.description}")
        print("Reminders:")
        for r in reminders:
            print(f"  ({r.priority}) {r.reminder_text}")

        print("\nAll Phase 1 checks passed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
