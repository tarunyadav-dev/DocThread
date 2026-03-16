
import argparse
import sys
from pathlib import Path

# Ensure Python can find our modules when running from the terminal
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ingestion_engine.shared_basics.file_io import save_raw_markdown
from ingestion_engine.shared_basics.sqlite_tracker import log_download
from ingestion_engine.shared_basics.chunker import chunk_markdown_documents
from ingestion_engine.shared_basics.chroma_manager import save_chunks_to_vector_db

# Import our new Tracer Bullet scrapers
from ingestion_engine.connectors.pandas_docs import PandasScraper
from ingestion_engine.connectors.react_docs import ReactScraper

def main():
    parser = argparse.ArgumentParser(description="DocThread Local Ingestion Engine")
    parser.add_argument("framework", type=str, help="The name of the documentation to scrape (e.g., 'pandas' or 'react')")
    args = parser.parse_args()

    framework = args.framework.lower()
    print(f"🚀 Starting ETL Pipeline for: {framework}")

    # 1. Route to the correct scraper
    if framework == "pandas":
        scraper = PandasScraper()
    elif framework == "react":
        scraper = ReactScraper()
    else:
        print(f"❌ Error: No connector found for '{framework}'.")
        return

    # Run the scrape (This proves internet -> schema works)
    documents = scraper.scrape()

    if not documents:
        print("⚠️ No documents scraped. Exiting.")
        return

    # 2. Save Raw Backup (Proves file_io works)
    save_raw_markdown(documents)

    # 3. Chunk the text (Proves LlamaIndex placeholder works)
    chunks = chunk_markdown_documents(documents)

    # 4. Save to Vector DB (Proves Chroma placeholder works)
    save_chunks_to_vector_db(chunks, framework)

    # 5. Log the success in SQLite (Proves SQLite works)
    log_download(framework, len(documents))
    
    print("🎉 Pipeline Complete!")

if __name__ == "__main__":
    main()