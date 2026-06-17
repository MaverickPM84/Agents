# 02 — High-Level Design (HLD) / Architecture

> The **boxes and arrows**: which components exist, how a request flows, and *why* we chose this shape.

## 1. Architecture style: 3-tier (client → API → data)
We separate the system into three layers, each with one job:

1. **Presentation (Streamlit)** — what the user sees. No business logic.
2. **Application/API (FastAPI + LangChain)** — the "brain": validation, URL extraction, summarisation, persistence orchestration.
3. **Data (SQLite)** + **External services (Groq)** — storage and the LLM.

Why: this is the most transferable architecture across the whole roadmap. Swapping the UI, the DB, or the LLM each touches only one layer.

## 2. Component diagram

```
        ┌──────────────────────────────────────────────────────────┐
        │                        USER (browser)                     │
        └───────────────────────────┬──────────────────────────────┘
                                     │ interacts
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │  FRONTEND  —  Streamlit app                               │
        │  • input box (text or URL)  • summarise button            │
        │  • result view  • history view                            │
        └───────────────────────────┬──────────────────────────────┘
                                     │ HTTP (JSON)  POST /summarise, GET /history
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │  BACKEND  —  FastAPI                                       │
        │                                                           │
        │   routes ──▶ services ──▶ ┌────────────────────────────┐  │
        │                           │ extractor (trafilatura)    │  │
        │                           │ summariser (LangChain)     │  │
        │                           │ llm_provider (abstraction) │──┼──▶ GROQ API
        │                           │ repository (SQLite access) │  │   (external LLM)
        │                           └────────────┬───────────────┘  │
        └────────────────────────────────────────┼─────────────────┘
                                                  │ SQL
                                                  ▼
                                   ┌────────────────────────────┐
                                   │  SQLite  (summaries table) │
                                   └────────────────────────────┘
```

## 3. Request flow (the main "summarise" path)
```
1. User enters text OR url in Streamlit, clicks "Summarise".
2. Streamlit sends POST /summarise  { "text": "...", "url": null }  (or url set).
3. FastAPI validates the request (exactly one of text/url; length limits).
4. If url: extractor fetches page → trafilatura returns clean body text.
   If text: use it directly.
5. summariser builds a prompt + calls llm_provider.summarise(text).
6. llm_provider (Groq impl) calls Groq via LangChain, returns summary string.
7. repository saves {source_type, source_ref, summary, created_at} to SQLite.
8. FastAPI returns { "id", "summary", "created_at" }.
9. Streamlit renders the summary; history view refreshes.
```

## 4. Why each layer is decoupled (the key design principle)
- **Streamlit calls HTTP, not Python functions.** So the backend could later be used by a mobile app or CLI unchanged.
- **The LLM sits behind `llm_provider`** — an interface with a `summarise(text) -> str` method. Groq is one implementation; Ollama will be another. *Nothing else in the code knows which LLM is used.* This is the **Strategy pattern** / **dependency inversion** — depend on an abstraction, not a concrete vendor.
- **DB access is isolated in a `repository`** module. If we move SQLite → Postgres later, only that module changes.

## 5. Technology choices & rationale
| Layer | Choice | Why | Alternative considered |
|-------|--------|-----|------------------------|
| UI | Streamlit | Fastest way to a data/AI UI in pure Python | React (more power, much more work) |
| API | FastAPI | Async, automatic validation (Pydantic) + auto docs | Flask (less built-in), Django (too heavy) |
| LLM orchestration | LangChain | Standard abstractions; eases v2 map-reduce | Calling Groq SDK directly (less reusable) |
| LLM | Groq `llama-3.3-70b-versatile` | Free, fast, 128K context | OpenAI (paid), local Llama 70B (too heavy) |
| DB | SQLite | Zero-config, file-based, perfect single-user | Postgres (needs a server) |
| URL extraction | trafilatura | Accurate, maintained | newspaper3k (unmaintained) |
| Packaging | Docker + compose | Identical runs anywhere; 2 services | Bare venv (not portable) |

## 6. Deployment topology (v1, local)
```
docker compose up
 ├── service: backend   (FastAPI, port 8000)   ── reads .env (GROQ_API_KEY, MODEL)
 │     └── volume: ./data/summaries.db  (SQLite persists outside the container)
 └── service: frontend  (Streamlit, port 8501) ── talks to backend at http://backend:8000
```
Key point: the **SQLite file lives on a mounted volume**, so data survives container restarts. The frontend reaches the backend by its compose service name (`backend`), not `localhost`.

## 7. Cross-cutting concerns
- **Config** via `.env` + a single `settings` module (12-factor: config in the environment).
- **Logging** at the API boundary (request received, errors).
- **Errors**: services raise typed exceptions; the API layer maps them to clean HTTP responses (see doc 04).
- **Testing seam**: because `llm_provider` is injected, tests substitute a fake — no network, no cost (see doc 06).
