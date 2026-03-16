import sys
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def peek_at_database(framework: str, query: str):
    # 1. Setup paths
    base_dir = Path(__file__).resolve().parent.parent
    chroma_dir = base_dir / "data" / "chroma_db" / framework.lower()

    if not chroma_dir.exists():
        print(f"❌ No database found at {chroma_dir}")
        return

    print(f"🔌 Connecting to {framework.upper()} Vector Database...")

    # 2. Load the AI Math Engine (must be the EXACT same one used to save)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 3. Load the Database (Read-Only Mode)
    vector_db = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=embeddings,
        collection_name=f"{framework.lower()}_docs"
    )

    # ... (keep the top part of the file the same) ...
    
    # 4. Perform a test search
    print(f"\n🔍 Searching for: '{query}'")
    results = vector_db.similarity_search(query, k=3) 

    print(f"\n🎯 Found {len(results)} matching chunks. Here is exactly what is inside them:\n")

    for i, doc in enumerate(results):
        print("=" * 70)
        print(f"🧱 CHUNK {i+1} | Source File: {doc.metadata.get('source_file', 'Unknown')}")
        print("-" * 70)
        
        print("🎒 METADATA (The Registry Backpack):")
        for key, value in doc.metadata.items():
            print(f"   * {key}: {value}")
            
        print("\n📝 CONTENT (The Actual Sliced Text):")
        # 🔥 REMOVED TRUNCATION: Let's see the whole thing to check the code blocks!
        print(doc.page_content) 
        print("=" * 70 + "\n")

if __name__ == "__main__":
    test_framework = "pandas"
    # 🔥 CHANGED QUERY: Let's force it to find a complex code example
    test_query = "Show me a code example of how to merge, join, or concatenate DataFrames"
    
    peek_at_database(test_framework, test_query)