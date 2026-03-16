from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    framework_name: str  # e.g., 'react' or 'pandas' so we search the right vector DB

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    FUTURE API ROUTE:
    This will eventually:
    1. Turn the user's message into a vector.
    2. Search ChromaDB for `request.framework_name`.
    3. Send the chunks to LiteLLM.
    4. Stream the text back to the frontend.
    """
    return {"message": f"[Placeholder] AI is ready to search {request.framework_name} docs for: '{request.message}'"}