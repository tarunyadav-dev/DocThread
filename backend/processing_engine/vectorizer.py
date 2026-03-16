import os
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from processing_engine.chunker import DocChunker

class DocVectorizer:
    def __init__(self, framework: str):
        self.framework = framework.lower()
        
        # Paths
        base_dir = Path(__file__).resolve().parent.parent
        self.raw_docs_dir = base_dir / "data" / "raw_docs" / self.framework
        
        # Save exact ChromaDB to the folder you requested
        self.chroma_dir = base_dir / "data" / "chroma_db" / self.framework
        
        # The AI Math Engine (Runs locally, free and fast)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.chunker = DocChunker()

    def process_and_store(self):
        if not self.raw_docs_dir.exists():
            print(f"❌ No raw docs found at {self.raw_docs_dir}")
            return

        all_chunks = []
        md_files = list(self.raw_docs_dir.glob("*.md"))
        
        print(f"🔍 Found {len(md_files)} files for {self.framework}. Starting processing...")

        # 1. THE LOOP: Process every file
        for i, file_path in enumerate(md_files):
            print(f"🔪 [{i+1}/{len(md_files)}] Slicing: {file_path.name}")
            chunks = self.chunker.chunk_file(file_path, self.framework)
            all_chunks.extend(chunks)

        if not all_chunks:
            print("⚠️ No chunks generated. Exiting.")
            return

        print(f"🧱 Total granular chunks created: {len(all_chunks)}")
        print(f"🧠 Converting text to math (Embeddings) and saving to DB...")

        # 2. THE DB INSERTION: Save to ChromaDB
        # We ensure the directory exists first
        os.makedirs(self.chroma_dir, exist_ok=True)
        
        vector_db = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            persist_directory=str(self.chroma_dir),
            collection_name=f"{self.framework}_docs"
        )
        
        print(f"✅ SUCCESS! Vector database saved at: {self.chroma_dir}")