from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter()

# Schema for the frontend request
class IngestRequest(BaseModel):
    framework_name: str

@router.post("/ingest")
async def trigger_ingestion(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    FUTURE API ROUTE:
    This will eventually import the logic from `ingestion_engine/run_terminal.py`
    and run it in the background so the user's browser doesn't time out.
    """
    
    # Placeholder for future logic:
    # background_tasks.add_task(run_etl_pipeline, request.framework_name)
    
    return {
        "status": "queued", 
        "message": f"Ingestion pipeline for '{request.framework_name}' will start in the background."
    }