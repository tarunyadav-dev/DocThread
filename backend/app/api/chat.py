# backend/app/api/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import traceback # 🔥 Added to pinpoint exact errors in Docker logs
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

router = APIRouter()

# --- GLOBAL CACHE ---
# Loading AI models takes seconds. We want to do it ONCE and keep it in memory.
VECTOR_STORE_CACHE = {}
EMBEDDINGS_MODEL = None

def get_vector_store(framework: str):
    global EMBEDDINGS_MODEL
    
    # If we already loaded this database, return it instantly
    if framework in VECTOR_STORE_CACHE:
        return VECTOR_STORE_CACHE[framework]

    base_dir = Path(__file__).resolve().parent.parent.parent
    chroma_dir = base_dir / "data" / "chroma_db" / framework

    if not chroma_dir.exists():
        raise FileNotFoundError(f"Database for {framework} not found at {chroma_dir}")

    # Load the math model only once
    if EMBEDDINGS_MODEL is None:
        print("⏳ Loading HuggingFace Embeddings Model into memory...")
        EMBEDDINGS_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"🔌 Connecting to ChromaDB for {framework}...")
    vector_db = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=EMBEDDINGS_MODEL,
        collection_name=f"{framework}_docs"
    )
    
    # Save to cache so the next search is lightning fast
    VECTOR_STORE_CACHE[framework] = vector_db
    return vector_db


# --- SCHEMAS ---
class SearchRequest(BaseModel):
    query: str
    framework_name: str
    top_k: int = 3 # How many chunks to return

class ChatRequest(BaseModel):
    message: str
    framework_name: str


# --- ENDPOINTS ---
@router.post("/chat/search")
async def raw_documentation_search(request: SearchRequest):
    """
    THE SYNTAX MAPPER API:
    Takes a query/code snippet, searches ChromaDB, and returns the exact 
    documentation chunks with their metadata.
    """
    framework = request.framework_name.lower()
    
    try:
        # Get the cached database
        vector_db = get_vector_store(framework)
        
        # Perform the search
        results = vector_db.similarity_search(request.query, k=request.top_k)
        
        # Format the output for Next.js
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
            
        return {"query": request.query, "results": formatted_results}
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 🔥 Print the exact error to the Docker logs so we aren't guessing!
        print("\n❌ CRITICAL SEARCH ERROR:")
        traceback.print_exc() 
        print("-" * 50)
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    FUTURE LITE-LLM ROUTE
    """
    return {
        "status": "placeholder",
        "message": f"AI Chat route prepared. Ready to connect LiteLLM for '{request.framework_name}'."
    }