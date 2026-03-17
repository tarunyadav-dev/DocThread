
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
# --- EXISTING SCRAPERS ---
from ingestion_engine.connectors.pandas_docs import PandasScraper
from ingestion_engine.connectors.react_docs import ReactScraper
from ingestion_engine.connectors.numpy_docs import NumpyScraper
from ingestion_engine.connectors.python_docs import PythonScraper
from ingestion_engine.connectors.nextjs_docs import NextjsScraper

# --- CORE LANGUAGES ---
from ingestion_engine.connectors.cpp_docs import CppScraper
from ingestion_engine.connectors.java_docs import JavaScraper
from ingestion_engine.connectors.go_docs import GoScraper
from ingestion_engine.connectors.rust_docs import RustScraper

# --- DATA SCIENCE & ML ---
from ingestion_engine.connectors.scikit_docs import ScikitLearnScraper
from ingestion_engine.connectors.matplotlib_docs import MatplotlibScraper
from ingestion_engine.connectors.seaborn_docs import SeabornScraper
from ingestion_engine.connectors.pytorch_docs import PytorchScraper

# --- BACKEND & INFRASTRUCTURE ---
from ingestion_engine.connectors.fastapi_docs import FastapiScraper
from ingestion_engine.connectors.express_docs import ExpressScraper
from ingestion_engine.connectors.postgres_docs import PostgresScraper
from ingestion_engine.connectors.redis_docs import RedisScraper

# --- FRONTEND (STATIC & DYNAMIC) ---
from ingestion_engine.connectors.tailwind_docs import TailwindScraper
from ingestion_engine.connectors.angular_docs import AngularScraper
from ingestion_engine.connectors.vue_docs import VueScraper
from ingestion_engine.connectors.typescript_docs import TypescriptScraper

# --- MOBILE, CLOUD & BIG DATA (DYNAMIC) ---
from ingestion_engine.connectors.flutter_docs import FlutterScraper
from ingestion_engine.connectors.reactnative_docs import ReactNativeScraper
from ingestion_engine.connectors.django_docs import DjangoScraper
from ingestion_engine.connectors.docker_docs import DockerScraper
from ingestion_engine.connectors.firebase_docs import FirebaseScraper
from ingestion_engine.connectors.tensorflow_docs import TensorflowScraper

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
    elif framework == "numpy":
        scraper = NumpyScraper()
    elif framework == "python":
        scraper = PythonScraper()
    elif framework == "nextjs":
        scraper = NextjsScraper()
        
    # --- CORE LANGUAGES ---
    elif framework == "cpp":
        scraper = CppScraper()
    elif framework == "java":
        scraper = JavaScraper()
    elif framework == "go":
        scraper = GoScraper()
    elif framework == "rust":
        scraper = RustScraper()

    # --- DATA SCIENCE & ML ---
    elif framework == "scikit":
        scraper = ScikitLearnScraper()
    elif framework == "matplotlib":
        scraper = MatplotlibScraper()
    elif framework == "seaborn":
        scraper = SeabornScraper()
    elif framework == "pytorch":
        scraper = PytorchScraper()

    # --- BACKEND & INFRASTRUCTURE ---
    elif framework == "fastapi":
        scraper = FastapiScraper()
    elif framework == "express":
        scraper = ExpressScraper()
    elif framework == "postgres":
        scraper = PostgresScraper()
    elif framework == "redis":
        scraper = RedisScraper()

    # --- FRONTEND ---
    elif framework == "tailwind":
        scraper = TailwindScraper()
    elif framework == "angular":
        scraper = AngularScraper()
    elif framework == "vue":
        scraper = VueScraper()
    elif framework == "typescript":
        scraper = TypescriptScraper()

    # --- MOBILE, CLOUD & BIG DATA ---
    elif framework == "flutter":
        scraper = FlutterScraper()
    elif framework == "reactnative":
        scraper = ReactNativeScraper()
    elif framework == "django":
        scraper = DjangoScraper()
    elif framework == "docker":
        scraper = DockerScraper()
    elif framework == "firebase":
        scraper = FirebaseScraper()
    elif framework == "tensorflow":
        scraper = TensorflowScraper()
        
    else:
        print(f"❌ Error: No connector found for '{framework}'.")
        print("Supported frameworks include: pandas, react, numpy, python, nextjs, cpp, java, go, rust, scikit, matplotlib, seaborn, pytorch, fastapi, express, postgres, redis, tailwind, angular, vue, typescript, flutter, reactnative, django, docker, firebase, tensorflow.")
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

