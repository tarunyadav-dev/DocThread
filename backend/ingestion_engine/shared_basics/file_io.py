import re
import os
from pathlib import Path
from typing import List
from ingestion_engine.connectors.base_connector import ScrapedDocument

def sanitize_filename(name: str) -> str:
    clean_name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', clean_name)

def save_raw_markdown(documents: List[ScrapedDocument]) -> str:
    # 1. GET ABSOLUTE BACKEND PATH
    # We go: shared_basics -> ingestion_engine -> backend
    this_file = Path(__file__).resolve()
    backend_root = this_file.parent.parent.parent
    
    # 2. DEFINE AND CREATE THE DATA DIRECTORY
    base_path = backend_root / "data" / "raw_docs"
    
    print(f"📂 [SYSTEM] Attempting to save to: {base_path}")

    # Ensure the directory exists (exist_ok=True means don't crash if it's there)
    base_path.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    
    for doc in documents:
        framework_folder = sanitize_filename(doc.framework)
        safe_title = sanitize_filename(doc.title)
        
        # Create framework-specific subfolder
        final_dir = base_path / framework_folder
        final_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = final_dir / f"{safe_title}.md"
        
        # 3. THE ACTUAL WRITE
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"---\ntitle: {doc.title}\nurl: {doc.url}\nframework: {doc.framework}\n---\n\n")
                f.write(doc.markdown_content)
            
            # Check if file actually exists after writing
            if file_path.exists():
                print(f"✅ [FILE WRITTEN]: {file_path}")
                saved_count += 1
            else:
                print(f"❌ [ERROR]: File system reported success but file is missing: {file_path}")
        except Exception as e:
            print(f"❌ [CRITICAL ERROR]: Could not write to disk: {e}")
            
    return str(base_path)