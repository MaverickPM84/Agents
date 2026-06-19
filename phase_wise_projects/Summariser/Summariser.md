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

Open Questions - 

1. What are pydantic models in the tech stack additions? How do they work ? What is the purpose ? why are they important ?

**Answer:**

A **Pydantic model** is a Python class that describes the *shape* of some data — what fields it has and what type each field should be. You define it once, and Pydantic automatically **validates** incoming data against that shape, **converts** values where sensible, and gives **clear errors** when the data is wrong.

```python
from pydantic import BaseModel

class SummariseRequest(BaseModel):
    text: str | None = None
    url: str | None = None
```

That class *is* a contract: "a summarise request has an optional `text` string and an optional `url` string."

**How they work — three things happen automatically:**
1. **Validation** — if someone sends `text: 123` (a number) where a string is expected, or forgets a required field, Pydantic rejects it instead of letting bad data flow deeper.
2. **Type coercion** — a field typed as `int` receiving the string `"5"` becomes `5`. Sensible conversions are free; nonsensical ones (`"hello"` → `int`) raise an error.
3. **Structured errors** — failures report *which field* and *what was wrong*; FastAPI turns these into clean HTTP 422 responses automatically.

**Purpose / why they matter here:** The request crosses a network boundary (Streamlit → HTTP → FastAPI). Anything could arrive at `/summarise`. Pydantic models are the **guard at the door**:
- **Request model** validates what comes *in*, so summariser code is guaranteed well-formed data — no scattered defensive checks.
- **Response model** guarantees what goes *out* is consistent, so Streamlit always knows what to expect back.

Three reasons specific to this build:
1. **Free with FastAPI** — FastAPI is *built on* Pydantic; declaring a model as the endpoint input gives validation, parsing, and error responses with zero extra code.
2. **Typed contract between layers** — same idea as "state keys are the contract between agents" in the ADK project; here Pydantic is the contract between Streamlit and FastAPI, letting them evolve independently.
3. **Testable** — the spec wants "request validation" tested; feed good/bad data, assert accept/reject. One of the `pytest` targets.

**One-line summary:** A Pydantic model is a typed, self-validating schema for data crossing the API boundary — it catches bad input early, documents the exact shape of requests/responses, and FastAPI uses it automatically.

---

2. In our use case, what validation is going to happen? (with an example)

**Answer:**

The `/summarise` endpoint accepts **either pasted text or a URL**, so the request model has two optional fields:

```python
class SummariseRequest(BaseModel):
    text: str | None = None
    url: str | None = None
```

What Pydantic checks at the door, before any summarising logic runs:

**1. Type validation — fields must be strings (or absent).**
```jsonc
{ "text": "Long meeting notes here..." }   // ✅ accepted
{ "text": 12345 }                          // ❌ rejected → 422 "input should be a valid string"
```

**2. Shape validation — the JSON must have the right structure.**
```jsonc
{ "article": "some text" }   // ❌ wrong field name → text and url both stay None
```

**3. Custom rule (specific to our use case) — exactly one of `text` or `url` must be provided.**
Plain typing can't express "one or the other, not neither/both", so add a validator:

```python
from pydantic import model_validator

class SummariseRequest(BaseModel):
    text: str | None = None
    url: str | None = None

    @model_validator(mode="after")
    def exactly_one_input(self):
        if not self.text and not self.url:
            raise ValueError("Provide either text or url.")
        if self.text and self.url:
            raise ValueError("Provide only one of text or url, not both.")
        return self
```

```jsonc
{ }                                              // ❌ "Provide either text or url."
{ "text": "hello", "url": "https://x.com" }      // ❌ "Provide only one of text or url, not both."
{ "url": "https://example.com/article" }         // ✅ accepted
```

**Why it matters for our flow** (`POST /summarise → (if URL: extract body) → summarise via Groq → save → return`): without validation, an empty or malformed request travels all the way down — wasting a Groq API call, possibly crashing inside `trafilatura`, or writing garbage to SQLite. With the model, bad requests are rejected instantly at the boundary, and the real logic is guaranteed exactly one valid input. Validation pushed to the edge, business logic stays clean.

 