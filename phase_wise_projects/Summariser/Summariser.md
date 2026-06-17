Summariser Chatbot - which can summarise any text, can be used for meeting notes or long articles.


Use Case - A user pastes a long article or text and wants to get a summary of it. The chatbot will process the text and return a summary of it.


Tech Stack -

Frontend - Streamlit App

Backend - Python

API - FastAPI

Framework - Langchain

Database - SQLlite

AI - Groq API/local llama 3.3 70B model


---


## v1 Spec (finalised)

Decisions below are locked for v1. Items marked (v2) are deferred but the code should be built so they slot in without a rewrite.

### Scope
- **Architecture:** Streamlit (UI) -> FastAPI (`/summarise`) -> LangChain (Groq) -> SQLite (history). The summariser logic lives behind the API, not in the UI.
- **Model:** Groq `llama-3.3-70b-versatile` (128K context, strong general model on the free tier). Fallback if rate-limited: `llama-3.1-8b-instant`. Model name lives in `.env`, never hardcoded.
- **Input:** user pastes raw text **or** an article URL. For a URL, extract the clean article body before summarising.
- **Long text:** v1 assumes input fits in one prompt (no chunking). (v2) handle longer-than-context inputs with LangChain map-reduce.
- **Summary style:** one hardcoded default. (v2) let the user choose length (short/medium/long) and format (bullets/paragraph).
- **Storage:** SQLite stores summary history the user can revisit. Single-user, local. No login.
- **Local models (Ollama):** deferred. The LLM sits behind a provider abstraction so a local Ollama model (e.g. `llama3.2:3b`) can be added later as a new provider class. (Llama 3.3 70B needs ~40GB+ RAM, too heavy for a laptop — local will use a smaller model.)

### Tech stack additions (beyond the original list)
- `python-dotenv` + `.env` — hold the Groq API key and model name.
- `requirements.txt` — pinned dependencies (rebuilds the exact environment anywhere).
- Pydantic models — FastAPI request/response validation (comes with FastAPI).
- `trafilatura` — extract the clean article body from a pasted URL (strips nav/ads/HTML noise). Chosen over `newspaper3k` (unmaintained).
- `venv` — per-project virtual environment isolating this project's packages.
- **Docker + docker-compose** — now **in v1 scope**. Two services (FastAPI backend, Streamlit frontend) defined in `docker-compose.yml`, run with `docker compose up`. Needs Docker Desktop installed to build/run; the files can be written before that.
- **Tests (`pytest`)** — now **in v1 scope**. Test the deterministic parts (URL extraction, SQLite history, request validation) directly; **mock** the LLM call so tests are fast, free, and deterministic.

### Why Docker + tests from phase 1
Easier to grow a small dockerised/tested app than to retrofit both onto a finished one, and both are core "complete product" skills that carry across the whole roadmap. Tests give the safety net to add v2 features (map-reduce, Ollama, user options) without silently breaking v1.

### Why FastAPI in v1
Separating the API (the product's "brain") from the UI (the "screen") is the core transferable skill across all five planned chatbots, and matches the roadmap goal of building complete products. Streamlit becomes a thin frontend that calls the `/summarise` endpoint.

### Target v1 flow
Streamlit form (text or URL) -> POST /summarise -> (if URL: extract body) -> LangChain summarise via Groq -> save to SQLite -> return summary -> Streamlit shows it + a history view.

### Concepts to learn (explained when we build)
- **trafilatura:** content extraction — turns raw, noisy article HTML into just the clean body text.
- **venv:** an isolated per-project Python so package versions don't clash between projects; `requirements.txt` records them for rebuilds.
- **Docker / docker-compose:** packages the whole app (OS + Python + packages + code) into an image that runs identically anywhere; compose runs the backend + frontend together.
- **Tests (pytest + mocking):** automated checks of real code; mocking replaces a real dependency (the LLM) with a fast, fake stand-in during the test.
- **Map-reduce / chunking (v2):** split long text into chunks that each fit the context window, summarise each (map), then summarise the summaries (reduce) into one final result.
- **Ollama (later):** runs LLMs locally — no API key, no cost, private, but hardware-limited.
