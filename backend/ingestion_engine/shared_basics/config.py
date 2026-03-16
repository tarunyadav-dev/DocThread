import os
from dotenv import load_dotenv
from pathlib import Path

# Go up two levels to find the root .env file (backend/ingestion_engine/shared_basics -> root)
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # You can add GEMINI_API_KEY or others here later
    
    # Database Paths
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "data/chroma_db")
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/docthread.db")
    RAW_DOCS_DIR = os.getenv("RAW_DOCS_DIR", "data/raw_docs")

settings = Settings()

# Fast fail: If we absolutely need a key to run the engine, check it here.
# if not settings.OPENAI_API_KEY:
#     print("⚠️ WARNING: OPENAI_API_KEY is missing from .env. Embeddings may fail.")