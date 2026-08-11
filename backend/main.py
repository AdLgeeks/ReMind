from fastapi import FastAPI

from database import init_db
from api.people import router as people_router
from api.faces import router as faces_router

app = FastAPI(title="Personal Memory OS - Phase 3 (Face embeddings)")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "phase": 3}


app.include_router(people_router)
app.include_router(faces_router)
