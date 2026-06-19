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


## 8. Answers to open questions (resolved)

### Q1. What is "persistence orchestration," why do we need it, what does it do?
"Persistence" = saving data so it survives after the request ends (here, into SQLite). "Orchestration" = coordinating the *order* of steps — when to save, what to save, and what to do if saving fails. So **persistence orchestration is the part of the backend that decides to write the summary to the DB at the right moment, then hands the saved record back to the caller.**

In our flow it's the glue across steps 5→8: "first summarise, **then** persist, **then** return the DB-generated `id` and `created_at`." The `repository` module does the raw SQL; the **service layer orchestrates** *when* it gets called.

Why we need it here:
- The **history view** is a core feature — a summary isn't in the history list until it's been written to SQLite.
- The response's `id` and `created_at` **only exist after the row is inserted** (the DB generates them), so saving is on the critical path of producing the response, not an afterthought.
- It keeps concerns isolated: the summariser doesn't know SQL exists; the repository doesn't know what an LLM is. The orchestrator sits above both and sequences them.

Open policy (resolved in doc 04): if summarisation succeeds but the DB write fails, do we still return the summary or error out? Orchestration is where that policy is decided.

### Q2. How does the backend service work — the flow in this use case?
FastAPI is organized in **layers, each with one job**; a request falls through them top to bottom:

```
HTTP request  POST /summarise  { "text": "...", "url": null }
      │
      ▼
┌─ routes ──────────────────────────────────────────────┐
│  • FastAPI receives the JSON                           │
│  • Pydantic validates (exactly one of text/url;        │
│    length within limits) → invalid = 422 immediately   │
└───────────────┬───────────────────────────────────────┘
                ▼
┌─ services (the orchestrator from Q1) ─────────────────┐
│   1. if url → call extractor; else use text           │
│   2. call summariser to get the summary               │
│   3. call repository to save it                        │
│   4. assemble the response object                     │
└───────┬───────────────┬───────────────┬──────────────┘
        ▼               ▼               ▼
   extractor        summariser       repository
  (trafilatura)   (LangChain →      (SQLite SQL)
   url→clean text  llm_provider→Groq)
                         │
                         ▼
                     GROQ API
      │
      ▼
HTTP response  { "id", "summary", "created_at" }
```

Use case ("user pastes a URL"):
1. **routes** receives the request; Pydantic confirms exactly one of text/url and length limits. Bad input dies here with a 422 — cheap and early.
2. **services** sees a URL → calls **extractor** (trafilatura fetches the page, returns clean body text, strips menus/ads/footers).
3. services passes that text to **summariser** → builds a prompt, calls **llm_provider** (Groq impl) via LangChain, gets the summary string.
4. services calls **repository** → inserts the row; SQLite returns the generated `id` and `created_at`.
5. services assembles `{ id, summary, created_at }`; **routes** serializes to JSON, returns 200.

Why this shape: each layer is independently swappable and testable — test `extractor` with no LLM, `repository` with no network, and substitute a fake `llm_provider` in tests (the "testing seam," §7).

### Q3. How does the frontend service work — the flow in this use case?
Streamlit is **presentation only**: it talks to the backend **over HTTP** and contains no business logic (no LangChain, SQL, or trafilatura).

```
┌─ Streamlit app (in the browser, via Streamlit server) ─┐
│ 1. Render: input box, "Summarise" button, result,     │
│    history list                                        │
│ 2. User pastes text/URL, clicks "Summarise"           │
│      ▼                                                 │
│ 3. Build JSON { text, url } → POST                    │
│    http://backend:8000/summarise                       │
│      ▼  (waits — show a spinner)                       │
│ 4. Receive { id, summary, created_at }                │
│      ▼                                                 │
│ 5. Display the summary                                 │
│ 6. GET /history → re-render the history list           │
└────────────────────────────────────────────────────────┘
```

Use case:
1. Streamlit draws the page (input, button, result panel, history panel).
2. User pastes content, clicks **Summarise**.
3. Streamlit packages the input as JSON and sends `POST /summarise`. In Docker the address is `http://backend:8000` — the compose **service name**, not `localhost`, because the containers talk over the compose network.
4. While waiting it shows a spinner; the response carries the `summary` and new `id`.
5. It renders the summary text.
6. It calls `GET /history` and re-renders the list so the new entry appears.

Why this way: because the UI only speaks HTTP/JSON, Streamlit could be replaced with React, a mobile app, or a CLI without changing the backend (§4).

> Beginner note: **Streamlit re-runs the whole script top-to-bottom on every interaction** (every click/widget change). "State" like the current summary or history is held in Streamlit's session state, and the POST/GET calls fire as part of that re-run. Mental model: *interaction → full script re-run → HTTP call → re-render.*

### Q1b. What does "repository" mean in "repository saves {source_type, source_ref, …}"?
**Not** a git repository. A **repository** (the design pattern) is the module whose only job is to read/write one kind of data to the database — the single place that knows the SQL for the `summaries` table. Think of it as a librarian for one shelf: you ask "save this summary" or "give me the last 20," and it handles the SQL behind the scenes. Nobody else writes SQL.

```python
class SummaryRepository:
    def save(self, source_type, source_ref, summary, created_at) -> int:
        # INSERT INTO summaries (...) VALUES (...);  returns new id
        ...
    def list_recent(self, limit=20) -> list[Summary]:
        # SELECT * FROM summaries ORDER BY created_at DESC LIMIT ?
        ...
```

So "repository saves {…} to SQLite" = the service hands those fields to `repository.save(...)`, which turns them into an `INSERT` and returns the new `id`. Payoff: **swappability** (SQLite→Postgres later changes only this one module, like `llm_provider` hides which LLM) and **testability** (swap a fake in-memory repository in tests — no real DB).

