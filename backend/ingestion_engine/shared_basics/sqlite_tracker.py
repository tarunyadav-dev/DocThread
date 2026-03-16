import sqlite3
from pathlib import Path

backend_root = Path(__file__).resolve().parent.parent.parent
DB_PATH = backend_root / "data" / "docthread.db"

def init_db():
    """Creates the SQLite database and the tracking table if they don't exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloaded_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            framework_name TEXT UNIQUE,
            pages_scraped INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_download(framework_name: str, pages_scraped: int):
    """Logs or updates the record of a downloaded framework."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Insert or overwrite the existing record for this framework
    cursor.execute("""
        INSERT INTO downloaded_docs (framework_name, pages_scraped, last_updated)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(framework_name) DO UPDATE SET 
            pages_scraped=excluded.pages_scraped,
            last_updated=CURRENT_TIMESTAMP
    """, (framework_name, pages_scraped))
    conn.commit()
    conn.close()
    print(f"✅ SQLite: Logged {framework_name} with {pages_scraped} pages.")