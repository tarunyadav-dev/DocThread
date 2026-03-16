# DocThread

**Bridging the gap between AI speed and official documentation.**

## Why we built this
AI is incredible at writing complex logic, but it leaves developers disconnected from the underlying syntax. DocThread maps AI-generated code directly to the exact lines in official documentation—allowing you to leverage the speed of AI while truly learning the foundational building blocks of your stack.

## Core Tech Stack
* **Frontend:** Next.js, Tailwind CSS, shadcn/ui
* **Backend:** Python, FastAPI, LiteLLM
* **Databases:** ChromaDB (Local Vector), SQLite
* **Infrastructure:** Docker Compose

## Quick Start
1. Clone the repository.
2. Copy `.env.example` to `.env` and add your API keys.
3. Run `docker compose up --build` (or `make dev`).
4. Open `http://localhost:3000`..