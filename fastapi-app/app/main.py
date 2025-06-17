from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import redis
import os

app = FastAPI()

# PostgreSQL setup
DATABASE_URL = "postgresql://postgres:password@db:5432/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Redis setup
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # <- default to 'redis'
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)


# DB model
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)

Base.metadata.create_all(bind=engine)

# Pydantic schema
class NoteCreate(BaseModel):
    title: str
    content: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/notes/")
def create_note(note: NoteCreate):
    db = SessionLocal()
    db_note = Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    redis_client.set(f"note:{db_note.id}", f"{db_note.title} - {db_note.content}")
    return {"id": db_note.id, "title": db_note.title, "content": db_note.content}

@app.get("/notes/{note_id}")
def get_note(note_id: int):
    try:
        cached = redis_client.get(f"note:{note_id}")
        if cached:
            return {"cached": True, "data": cached.decode("utf-8")}
    except Exception as e:
        print(f"Redis error: {e}")

    db = SessionLocal()
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        redis_client.set(f"note:{note_id}", f"{db_note.title} - {db_note.content}")
    except Exception as e:
        print(f"Redis set error: {e}")

    return {"cached": False, "id": db_note.id, "title": db_note.title, "content": db_note.content}
