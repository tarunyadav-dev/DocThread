DocThread/
│
├── .github/                        # GitHub Actions, Issue Templates, and PR Rules
│   ├── ISSUE_TEMPLATE/             # Forms for users reporting bugs or requesting features
│   └── workflows/                  # CI/CD pipelines (e.g., auto-checking code formatting)
│
├── docs/                           # Project documentation
│   ├── folder_file.md              # THIS FILE: The living architecture document
│   └── architecture.md             # High-level system design and data flow diagrams
│
├── scripts/                        # Utility scripts for local development
│   └── reset_db.sh                 # Quick script to wipe local SQLite/ChromaDB for fresh testing
│
├── frontend/                       # NEXT.JS & TYPESCRIPT UI APPLICATION
│   ├── public/                     # Static assets (images, favicon)
│   ├── src/
│   │   ├── app/                    # Next.js App Router (Pages and Layouts)
│   │   │   ├── layout.tsx          # Global HTML shell and providers (Theme, Auth state)
│   │   │   ├── page.tsx            # The main Workspace UI (Chat + Traceability View)
│   │   │   └── globals.css         # Global Tailwind CSS imports
│   │   │
│   │   ├── components/             # Reusable React Components
│   │   │   ├── ui/                 # shadcn/ui components (Buttons, Inputs, Dialogs)
│   │   │   ├── chat/               # AI chat interface components
│   │   │   └── workspace/          # Side-by-side code/doc viewer components
│   │   │
│   │   ├── hooks/                  # Custom React Hooks
│   │   │   └── use-chat-stream.ts  # Logic for handling real-time AI typing from the backend
│   │   │
│   │   ├── lib/                    # Utility functions
│   │   │   └── utils.ts            # Common helpers (e.g., Tailwind class merging)
│   │   │
│   │   └── types/                  # TypeScript Interfaces
│   │       └── index.ts            # Definitions for Data Models (e.g., ChatMessage, DocChunk)
│   │
│   ├── next.config.mjs             # Next.js configuration settings
│   ├── tailwind.config.ts          # Tailwind styling rules and custom colors
│   ├── tsconfig.json               # TypeScript compiler strictness rules
│   ├── package.json                # Frontend dependencies (React, Tailwind, Lucide Icons)
│   └── Dockerfile                  # Instructions to containerize the Next.js app
│
├── backend/                        # PYTHON FASTAPI APPLICATION
│   ├── app/                        # Main application code
│   │   ├── __init__.py             # Marks directory as a Python package
│   │   ├── main.py                 # The FastAPI entry point (runs the server)
│   │   │
│   │   ├── api/                    # API Routes (Endpoints Next.js talks to)
│   │   │   ├── chat.py             # POST /api/chat -> Handles RAG and AI streaming
│   │   │   ├── ingest.py           # POST /api/ingest -> Triggers scrapers
│   │   │   └── bookmarks.py        # GET/POST /api/bookmarks -> SQLite operations
│   │   │
│   │   ├── core/                   # App Configuration
│   │   │   └── config.py           # Loads environment variables (BYOK keys)
│   │   │
│   │   ├── connectors/             # THE SCRAPING ENGINE (Pre-built Plugins)
│   │   │   ├── base.py             # Abstract base class all connectors must follow
│   │   │   ├── react_docs.py       # Crawl4AI scraper specifically tuned for React
│   │   │   └── pandas_docs.py      # BeautifulSoup scraper specifically tuned for Pandas
│   │   │
│   │   ├── services/               # Core Business Logic
│   │   │   ├── ai.py               # LiteLLM wrapper for talking to OpenAI/Anthropic/Gemini
│   │   │   └── chunking.py         # LlamaIndex logic to slice Markdown into readable chunks
│   │   │
│   │   └── db/                     # Database Managers
│   │       ├── vector_store.py     # ChromaDB logic (saving/searching doc chunks locally)
│   │       └── local_store.py      # SQLite logic (saving user bookmarks locally)
│   │
│   ├── data/                       # Local database storage (IGNORED BY GIT)
│   │   ├── chroma_db/              # Where the vector files actually live on disk
│   │   └── docthread.db            # The SQLite file for user data
│   │
│   ├── requirements.txt            # Python dependencies (FastAPI, Crawl4AI, ChromaDB, LiteLLM)
│   └── Dockerfile                  # Instructions to containerize the Python backend
│
├── .env.example                    # Template for API keys (e.g., OPENAI_API_KEY=...)
├── .gitignore                      # Blocks node_modules, __pycache__, and real .env files
├── docker-compose.yml              # Wires frontend and backend together on the same network
└── README.md                       # The Project Homepage (Why we built this, how to install)