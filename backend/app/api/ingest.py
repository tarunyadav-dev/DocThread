# backend/app/api/ingest.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

# Import our custom engines
from ingestion_engine.connectors.pandas_docs import PandasScraper
from ingestion_engine.connectors.react_docs import ReactScraper
from processing_engine.vectorizer import DocVectorizer

router = APIRouter()

class FrameworkRequest(BaseModel):
    framework_name: str

# --- BACKGROUND WORKER FUNCTIONS ---
def run_scraper(framework: str):
    print(f"⚙️ [BACKGROUND] Starting Scraper for {framework}...")
    if framework.lower() == "pandas":
        scraper = PandasScraper()
    elif framework.lower() == "react":
        scraper = ReactScraper()
    else:
        print(f"❌ [BACKGROUND] Unknown framework: {framework}")
        return
    scraper.scrape()
    print(f"✅ [BACKGROUND] Scrape complete for {framework}.")

def run_vectorizer(framework: str):
    print(f"⚙️ [BACKGROUND] Starting Vectorizer for {framework}...")
    vectorizer = DocVectorizer(framework=framework.lower())
    vectorizer.process_and_store()
    print(f"✅ [BACKGROUND] Vectorization complete for {framework}.")

def run_full_pipeline(framework: str):
    run_scraper(framework)
    run_vectorizer(framework)

# --- API ENDPOINTS ---

@router.post("/ingest/scrape")
async def trigger_scrape_only(request: FrameworkRequest, background_tasks: BackgroundTasks):
    """Triggers ONLY the web scraper (Downloads .md files)"""
    background_tasks.add_task(run_scraper, request.framework_name)
    return {"status": "queued", "action": "scraping", "framework": request.framework_name}

@router.post("/ingest/vectorize")
async def trigger_vectorize_only(request: FrameworkRequest, background_tasks: BackgroundTasks):
    """Triggers ONLY the vectorizer (Converts .md to ChromaDB)"""
    background_tasks.add_task(run_vectorizer, request.framework_name)
    return {"status": "queued", "action": "vectorizing", "framework": request.framework_name}

@router.post("/ingest/full")
async def trigger_full_pipeline(request: FrameworkRequest, background_tasks: BackgroundTasks):
    """Triggers the FULL pipeline (Scrape -> Vectorize)"""
    background_tasks.add_task(run_full_pipeline, request.framework_name)
    return {"status": "queued", "action": "full_pipeline", "framework": request.framework_name}
