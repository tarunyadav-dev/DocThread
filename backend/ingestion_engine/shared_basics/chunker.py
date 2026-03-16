from typing import List
from ingestion_engine.connectors.base_connector import ScrapedDocument

def chunk_markdown_documents(documents: List[ScrapedDocument]) -> List[dict]:
    """
    TODO: Implement LlamaIndex MarkdownNodeParser here.
    Takes the raw ScrapedDocuments and slices them by Markdown headers (##).
    Returns a list of dictionaries (the chunks) ready for ChromaDB.
    """
    print(f"⚙️ Chunker: Slicing {len(documents)} documents into smaller AI chunks...")
    # Placeholder logic
    chunks = []
    for doc in documents:
        chunks.append({
            "text": doc.markdown_content[:200] + "... [CHUNKED]", # Fake chunk for now
            "metadata": {"title": doc.title, "url": doc.url, "framework": doc.framework}
        })
    return chunks