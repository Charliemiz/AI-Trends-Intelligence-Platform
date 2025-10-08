from typing import Union
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv, find_dotenv
from perplexity_functions import perplexity_search, perplexity_summarize
from fastapi.middleware.cors import CORSMiddleware

PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"

load_dotenv(find_dotenv()) 
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Set DATABASE_URL in .env")

# SQLAlchemy engine + session factory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

app = FastAPI()

ALLOWED_ORIGINS = [
    "https://ai-trends-intelligence-platform-66rzjvtc2.vercel.app",  # hosted frontend
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# For creating a new database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/summary/add")
def add_summary(url: str, summary: str, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("INSERT INTO summary (url, summary) VALUES (:url, :summary)"),
            {"url": url, "summary": summary},
        )
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/perplexity/search")
def api_perplexity_search(query: str, count: int = 5):
    try:
        result = perplexity_search(query, count)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))