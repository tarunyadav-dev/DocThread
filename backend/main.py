# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, ingest
from app.api.settings_api import router as settings_router
from app.api.chat import router as chat_router

app = FastAPI(title="DocThread API")

# 🛡️ THE GATES: Allow Next.js (localhost:3000) to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect our modular routes
app.include_router(chat.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(settings_router, prefix="/api", tags=["Settings"])


@app.get("/")
def read_root():
    return {"status": "DocThread Backend is Online!"}