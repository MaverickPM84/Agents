# 03 — Low-Level Design (LLD)

> Inside the boxes: folder structure, each module's responsibility, the key interfaces, the DB schema, and config. This is the blueprint coding follows.

## 1. Folder structure
```
Summariser/
├── docs/                      # these planning documents
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, startup, router include
│   │   ├── config.py          # settings loaded from .env (pydantic-settings)
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── routes.py          # HTTP endpoints (thin; calls services)
│   │   ├── services/
│   │   │   ├── extractor.py   # URL -> clean text (trafilatura)
│   │   │   └── summariser.py  # text -> summary (orchestrates llm_provider)
│   │   ├── llm/
│   │   │   ├── base.py        # LLMProvider interface (abstract)
│   │   │   ├── groq_provider.py     # Groq implementation (LangChain)
│   │   │   └── factory.py     # picks provider from config
│   │   ├── db/
│   │   │   ├── database.py    # connection/session setup
│   │   │   └── repository.py  # save/list/get summaries (SQL lives here only)
│   │   └── errors.py          # typed exceptions
│   ├── tests/                 # pytest (mirrors app/ structure)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── streamlit_app.py       # UI; calls backend via httpx/requests
│   ├── api_client.py          # thin wrapper around backend HTTP calls
│   ├── requirements.txt
│   └── Dockerfile
├── data/                      # SQLite file lives here (gitignored)
├── docker-compose.yml
├── .env.example               # template (committed); real .env is gitignored
├── .gitignore
└── README.md
```
**Why split backend/frontend into separate folders + Dockerfiles?** They are independent deployables with different dependencies. Keeping them apart enforces the "UI calls API over HTTP" boundary physically.

## 2. Module responsibilities (single responsibility each)
| Module | Responsibility | Does NOT |
|--------|----------------|----------|
| `routes.py` | Parse/validate HTTP, call a service, shape response | Contain business logic or SQL |
| `services/extractor.py` | Fetch URL + extract clean body text | Know about HTTP/DB |
| `services/summariser.py` | Build prompt, call LLM provider, return summary | Know which LLM vendor |
| `llm/base.py` | Define the provider contract | — |
| `llm/groq_provider.py` | Implement contract using Groq via LangChain | Be referenced directly elsewhere |
| `db/repository.py` | All SQL (insert/list/get) | Contain business rules |
| `config.py` | Load & expose settings | — |

## 3. The key abstraction — `LLMProvider` interface
This is the heart of "swap Groq ↔ Ollama without touching anything else."

```python
# llm/base.py
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def summarise(self, text: str) -> str:
        """Return a summary of `text`. Raises LLMError on failure."""

# llm/groq_provider.py
class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self._llm = ChatGroq(api_key=api_key, model=model)  # LangChain
    def summarise(self, text: str) -> str:
        prompt = SUMMARISE_PROMPT.format(text=text)
        return self._llm.invoke(prompt).content

# llm/factory.py
def get_provider(settings) -> LLMProvider:
    if settings.llm_backend == "groq":
        return GroqProvider(settings.groq_api_key, settings.model_name)
    # future: if "ollama": return OllamaProvider(...)
```
The summariser depends only on `LLMProvider`. Tests pass a `FakeProvider` that returns a canned string — no network. (This is **dependency injection**.)

## 4. Data model & DB schema
One table is enough for v1.

```sql
CREATE TABLE summaries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type  TEXT    NOT NULL CHECK (source_type IN ('text','url')),
    source_ref   TEXT,            -- the URL, or NULL/preview for pasted text
    input_chars  INTEGER NOT NULL,
    summary      TEXT    NOT NULL,
    model        TEXT    NOT NULL,
    created_at   TEXT    NOT NULL  -- ISO-8601 timestamp
);
```
- We store `source_type` + `source_ref` so history can show "from URL X" vs "pasted text".
- `model` is recorded for traceability (which model produced this).
- We **don't** store the full raw input in v1 (privacy + size); a short preview is enough. (Revisit in v2 if needed.)

## 5. Configuration (`config.py`)
Loaded once from `.env` using `pydantic-settings`:
```
GROQ_API_KEY=...           # secret
LLM_BACKEND=groq           # groq | ollama (future)
MODEL_NAME=llama-3.3-70b-versatile
FALLBACK_MODEL=llama-3.1-8b-instant
DB_PATH=./data/summaries.db
MAX_INPUT_CHARS=40000      # guard for v1 single-prompt assumption
REQUEST_TIMEOUT_SECONDS=30
```
`.env.example` is committed with placeholder values; the real `.env` is gitignored.

## 6. Validation rules (enforced in `schemas.py`)
- Exactly one of `text` / `url` is provided (not both, not neither).
- `text` length ≤ `MAX_INPUT_CHARS` (else 422 → friendly message).
- `url` must be a valid http(s) URL.

## 7. Error handling (`errors.py`)
Typed exceptions, mapped to HTTP by the API layer (doc 04):
| Exception | Meaning | HTTP |
|-----------|---------|------|
| `InvalidInputError` | bad/empty/over-length input | 422 |
| `ExtractionError` | URL fetch/extract failed or empty | 422 |
| `LLMError` | provider/network failure | 502 |
| (unexpected) | bug | 500 |

## 8. Summarisation prompt (v1, fixed)
Stored as a constant so v2 can parameterise it:
```
You are a precise summariser. Summarise the text below into a clear,
concise summary that captures the key points and any decisions or action
items. Do not add information that is not in the text.

TEXT:
{text}
```
