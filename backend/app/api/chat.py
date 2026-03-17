from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import traceback
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from fastapi.responses import StreamingResponse
import litellm
import os
from dotenv import load_dotenv
from app.core.config_manager import load_settings

load_dotenv()
router = APIRouter()

# --- GLOBAL CACHE ---
VECTOR_STORE_CACHE = {}
EMBEDDINGS_MODEL = None

def get_vector_store(framework: str):
    global EMBEDDINGS_MODEL
    if framework in VECTOR_STORE_CACHE:
        return VECTOR_STORE_CACHE[framework]

    base_dir = Path(__file__).resolve().parent.parent.parent
    chroma_dir = base_dir / "data" / "chroma_db" / framework

    if not chroma_dir.exists():
        raise FileNotFoundError(f"Database for {framework} not found at {chroma_dir}")

    if EMBEDDINGS_MODEL is None:
        print("⏳ Loading HuggingFace Embeddings (all-MiniLM-L6-v2)...")
        EMBEDDINGS_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_db = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=EMBEDDINGS_MODEL,
        collection_name=f"{framework}_docs"
    )
    
    VECTOR_STORE_CACHE[framework] = vector_db
    return vector_db

# --- SCHEMAS ---
class SearchRequest(BaseModel):
    query: str
    framework_name: str
    top_k: int = 3

class ChatRequest(BaseModel):
    message: str
    framework_name: str
    model: str = "google/gemini-2.0-flash-lite-preview-02-05:free"

# --- ENDPOINTS ---
@router.post("/chat/search")
async def raw_documentation_search(request: SearchRequest):
    framework = request.framework_name.lower()
    try:
        vector_db = get_vector_store(framework)
        results = vector_db.similarity_search(request.query, k=request.top_k)
        return {
            "query": request.query, 
            "results": [{"content": d.page_content, "metadata": d.metadata} for d in results]
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ... (Keep all your existing imports) ...
from app.core.config_manager import load_settings # <--- ADD THIS IMPORT

# ... (Keep get_vector_store and raw_documentation_search exactly the same) ...

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    framework = request.framework_name.lower()
    
    # 🌟 LOAD SETTINGS DYNAMICALLY
    settings = load_settings()
    my_api_key = settings.get("api_key", "")
    provider = settings.get("provider", "openrouter")
    
    # If the user passed a model from the UI, use it. Otherwise, use settings.
    target_model = request.model if request.model else settings.get("model")
    
    try:
        # 1. RAG Retrieval
        vector_db = get_vector_store(framework)
        docs = vector_db.similarity_search(request.message, k=4)
        
        context_text = "\n\n---\n\n".join([
            f"SOURCE_FILE: {doc.metadata.get('source_file', 'Unknown')}\n{doc.page_content}" 
            for doc in docs
        ])
        
        # 2. Strict Prompting
        system_prompt = f"""You are DocThread, a high-precision Documentation Analyzer.
        
Your response MUST follow this exact format:

### 🧠 EXPERT ANALYSIS
(Provide your detailed, intelligent explanation here using your full knowledge.)

### 📑 DOCUMENTATION REFERENCE
**Source File:** [Insert Filename from context here]
**Relevant Snippet:** [Insert the most relevant 1-2 lines from the chunk here]

---
STRICT RULES:
1. If the user asks something NOT in the docs, you must still provide the ANALYSIS but state "No local documentation match found" in the REFERENCE section.
2. Always keep the REFERENCE section short and technical.

LOCAL DOCUMENTATION CHUNKS:
{context_text}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]

        # 3. Model ID & Provider Formatting (Handling Ollama vs OpenRouter)
        # 3. Model ID & Provider Formatting (Handling Ollama vs OpenRouter vs Gemini)
        api_base = None
        if provider == "ollama":
            model_name = f"ollama/{target_model}"
            api_base = settings.get("ollama_base_url")
        elif provider == "gemini":
            # LiteLLM uses the 'gemini/' prefix for native Google AI Studio keys
            model_name = f"gemini/{target_model}" if not target_model.startswith("gemini/") else target_model
        elif provider == "openrouter":
            model_name = f"openrouter/{target_model}" if not target_model.startswith("openrouter/") else target_model
        else:
            model_name = target_model # Fallback for OpenAI, Anthropic, etc.

        async def response_generator():
            try:
                response = await litellm.acompletion(
                    model=model_name,
                    messages=messages,
                    stream=True,
                    api_key=my_api_key,
                    api_base=api_base # Required for Ollama
                )
                async for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            except Exception as e:
                yield f"AI_ERROR: {str(e)}"

        return StreamingResponse(response_generator(), media_type="text/event-stream")

    except Exception as e:
        print(f"CRITICAL: {e}")
        raise HTTPException(status_code=500, detail=str(e))