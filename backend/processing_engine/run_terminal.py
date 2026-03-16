import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from processing_engine.vectorizer import DocVectorizer

def main():
    if len(sys.argv) < 2:
        print("⚠️ Usage: python backend/processing_engine/run_terminal.py [framework_name]")
        print("Example: python backend/processing_engine/run_terminal.py react")
        sys.exit(1)

    framework = sys.argv[1].lower()
    
    print("========================================")
    print(f"🚀 DOC-THREAD VECTORIZER: {framework.upper()}")
    print("========================================")
    
    vectorizer = DocVectorizer(framework=framework)
    vectorizer.process_and_store()

if __name__ == "__main__":
    main()