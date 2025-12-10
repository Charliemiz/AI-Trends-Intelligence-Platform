"""Application entrypoint and FastAPI app configuration.

This module creates the FastAPI app instance, configures CORS origins, and
mounts the API router used by the frontend.

Variables
---------
app
    The FastAPI application instance used by ASGI servers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router

ALLOWED_ORIGINS = [
    "https://ai-trends-intelligence-platform.vercel.app",
    "https://ai-trends-intelligence-pl-git-263e86-charlies-projects-a3f87fbc.vercel.app",
    "https://ai-trends-intelligence-platform-kcanrbje9.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")