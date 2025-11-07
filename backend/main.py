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
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)