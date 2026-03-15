# DocThread System Manifest
*Last Updated: March 2026*

This document tracks all system-level software, frameworks, and libraries required to run DocThread, along with the reasoning for why they were chosen.

## 1. Core System Requirements (The Engine)
These must be installed on the host machine to develop or run the application.
* **Docker Desktop:** The orchestrator. Runs both the frontend and backend in isolated, identical containers so the app works flawlessly on any OS.
* **Node.js (LTS):** The JavaScript runtime required to install and run the Next.js frontend ecosystem.
* **Python (v3.11 / v3.12):** The native language of our AI and data-processing backend. 

## 2. Frontend Stack (Next.js UI)
*Located in `/frontend/package.json`*
* **Next.js (App Router):** The core React framework handling routing and UI rendering.
* **Tailwind CSS:** Utility-first CSS framework for rapid, standard-compliant styling.
* **shadcn/ui:** Unstyled, accessible UI components (buttons, dialogs, inputs) that we own and can customize completely.
* **ai (Vercel AI SDK):** Manages the complex logic of streaming text word-by-word from our Python backend to the chat interface.
* **lucide-react:** The industry-standard SVG icon library.

## 3. Backend Stack (Python API & AI)
*Located in `/backend/requirements.txt`*
* **FastAPI:** The high-performance API framework that connects our Python logic to our Next.js UI. 
* **uvicorn:** The lightning-fast web server that actually runs the FastAPI application.
* **python-dotenv:** Loads our secret API keys from the `.env` file into the application.
* **litellm:** The "Bring Your Own Key" (BYOK) router. It standardizes API calls so we can swap between OpenAI, Anthropic, and Gemini without changing our core code.
* **chromadb:** Our local vector database. It stores the chunked documentation and allows the AI to perform lightning-fast semantic searches.
* **crawl4ai:** The modern, AI-optimized web scraper used for extracting markdown from complex, JavaScript-heavy documentation sites.
* **llama-index:** The data framework used to cleanly slice large markdown files into smaller, AI-readable chunks.
* **beautifulsoup4 & requests:** The lightweight fallback scrapers for simple, static HTML documentation sites.