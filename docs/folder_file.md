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