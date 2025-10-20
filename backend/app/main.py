from fastapi import FastAPI
from app.api.routes import ingest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Insights Dashboard API")
app.include_router(ingest.router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or list your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)