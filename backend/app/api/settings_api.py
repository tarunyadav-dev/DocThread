from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config_manager import load_settings, save_settings

router = APIRouter()

class SettingsUpdate(BaseModel):
    provider: str
    model: str
    api_key: str
    ollama_base_url: str

@router.get("/settings")
async def get_settings():
    """Fetches the current LLM configuration."""
    return load_settings()

@router.post("/settings")
async def update_settings(settings: SettingsUpdate):
    """Updates the LLM configuration from the frontend."""
    save_settings(settings.dict())
    return {"status": "success", "message": "Settings saved successfully."}