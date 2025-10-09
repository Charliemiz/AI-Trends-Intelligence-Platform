from fastapi import FastAPI
from app.api.routes import ingest

app = FastAPI(title="AI Insights Dashboard API")

app.include_router(ingest.router, prefix="/api")
