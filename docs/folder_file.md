DocThread/
│
├── .github/                        # GitHub configurations
│   ├── ISSUE_TEMPLATE/             # Forms for users reporting bugs
│   └── workflows/                  # CI/CD automation scripts
│
├── backend/                        # PYTHON FASTAPI ENGINE
│   ├── __pycache__/                # (Auto-generated) Python compilation cache
│   ├── .venv/                      # (Auto-generated) Isolated Python environment
│   ├── data/                       # Local database storage (ChromaDB / SQLite)
│   ├── Dockerfile                  # Instructions to build the Python container
│   ├── main.py                     # Entry point for the FastAPI server
│   └── requirements.txt            # List of Python dependencies
│
├── docs/                           # PROJECT DOCUMENTATION
│   ├── folder_file.md              # THIS FILE: Maps out the repository structure
│   └── system_manifest.md          # Lists out our installed tech stack
│
├── frontend/                       # NEXT.JS UI APPLICATION
│   ├── .next/                      # (Auto-generated) Next.js build cache
│   ├── app/                        # Main React application routes and layouts
│   ├── components/                 # Reusable React UI elements (shadcn, etc.)
│   ├── lib/                        # Utility functions and helpers
│   ├── node_modules/               # (Auto-generated) Downloaded JS packages
│   ├── public/                     # Static assets (images, icons)
│   ├── components.json             # Configuration for shadcn/ui components
│   ├── Dockerfile                  # Instructions to build the Next.js container
│   ├── eslint.config.mjs           # Rules for keeping JavaScript code clean/standard
│   ├── next-env.d.ts               # (Auto-generated) TypeScript definitions for Next.js
│   ├── next.config.ts              # Core Next.js engine settings
│   ├── package-lock.json           # (Auto-generated) Exact version lock for JS packages
│   ├── package.json                # List of Node.js dependencies and run scripts
│   ├── postcss.config.mjs          # CSS processing engine settings (used by Tailwind)
│   └── tsconfig.json               # TypeScript compiler rules
│
├── my_random/                      # Personal workspace/scratchpad
├── scripts/                        # Automation scripts for local development
│
├── .env                            # Active API keys and secrets (IGNORED BY GIT)
├── .env.example                    # Template for secrets to share with other devs
├── .gitattributes                  # Normalizes line endings across Windows/Mac
├── .gitignore                      # Shield preventing junk files from hitting GitHub
├── docker-compose.yml              # Wires frontend and backend together via Docker
├── learning.txt                    # Personal learning notes and scratchpad
├── LICENSE                         # Legal open-source protection (MIT)
├── Makefile                        # Dev shortcuts (e.g., `make dev`)
└── README.md                       # The Project Homepage (Setup instructions & "Why")



backend/                        # PYTHON FASTAPI ENGINE & ETL PIPELINE
│
├── __pycache__/                # (Auto-generated) Python compilation cache
├── .venv/                      # (Auto-generated) Isolated Python environment
│
├── data/                       # LOCAL STORAGE
│   ├── raw_docs/               # Saves raw .md files as a local backup cache
│   ├── chroma_db/              # (Auto-generated) Vector embeddings for AI search
│   └── docthread.db            # SQLite database file for tracking downloads
│
├── ingestion_engine/           # THE ETL PIPELINE (Run from terminal)
│   ├── run_terminal.py         # The Main Ingestor: Type `python run_terminal.py react`
│   │
│   ├── shared_basics/          # Common tools used by all scrapers
│   │   ├── __init__.py         # Makes this folder a Python module
│   │   ├── file_io.py          # Logic to save raw text to `data/raw_docs/`
│   │   ├── chunker.py          # LlamaIndex logic to safely split Markdown
│   │   ├── chroma_manager.py   # Logic to save/wipe vector data
│   │   └── sqlite_tracker.py   # Logic to log "React 18 downloaded successfully"
│   │
│   └── connectors/             # THE SCRAPERS (One file per documentation)
│       ├── __init__.py         # Makes this folder a Python module
│       ├── base_connector.py   # The "Rulebook" template every scraper must follow
│       ├── react_docs.py       # Specific Crawl4AI script for React
│       └── pandas_docs.py      # Specific BeautifulSoup script for Pandas
│
├── app/                        # (FUTURE) THE API BRIDGE
│   └── api/
│       ├── __init__.py         
│       ├── chat_placeholder.py # Blank file: Future RAG/AI logic
│       └── ingest_placeholder.py # Blank file: Future API route to trigger the ETL pipeline
│
├── Dockerfile                  # Instructions to build the Python container
├── main.py                     # Entry point for the FastAPI server
└── requirements.txt            # List of Python dependencies