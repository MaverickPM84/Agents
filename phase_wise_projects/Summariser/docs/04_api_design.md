# 04 — API Design

> The **contract** between frontend and backend. Once fixed, both sides build against it independently. FastAPI auto-generates interactive docs for this at `/docs`.

## 1. Conventions
- Base URL (local): `http://localhost:8000`
- All requests/responses are JSON.
- Timestamps are ISO-8601 UTC strings.
- Errors share one consistent shape (section 5).

## 2. Endpoints overview
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness check (is the API up?) |
| POST | `/summarise` | Summarise text or a URL |
| GET | `/history` | List past summaries (newest first) |
| GET | `/history/{id}` | Get one summary by id |

---

## 3. POST /summarise
Summarise either pasted text or an article URL. **Exactly one** of `text`/`url` must be set.

### Request body
```json
{
  "text": "Long text to summarise...",
  "url": null
}
```
or
```json
{
  "text": null,
  "url": "https://example.com/article"
}
```

### Field rules
| Field | Type | Rules |
|-------|------|-------|
| `text` | string \| null | non-empty if provided; ≤ MAX_INPUT_CHARS |
| `url`  | string \| null | valid http(s) URL if provided |

### Success — 200
```json
{
  "id": 12,
  "summary": "The article argues that ...",
  "source_type": "url",
  "source_ref": "https://example.com/article",
  "model": "llama-3.3-70b-versatile",
  "elapsed_ms": 3214,
  "created_at": "2026-06-17T10:32:11Z"
}
```
`elapsed_ms` (FR9) is the server-side time to produce the summary, in milliseconds; the UI displays it as seconds (e.g. "3.2s").

### Failure examples
- `422` — both/neither of text/url, empty text, over-length, invalid URL, or extraction returned nothing.
- `502` — LLM/provider failure.

---

## 4. GET /history  and  GET /history/{id}

### GET /history?limit=20&offset=0 — 200
```json
{
  "items": [
    {
      "id": 12,
      "source_type": "url",
      "source_ref": "https://example.com/article",
      "summary": "The article argues that ...",
      "model": "llama-3.3-70b-versatile",
      "elapsed_ms": 3214,
      "created_at": "2026-06-17T10:32:11Z"
    }
  ],
  "limit": 20,
  "offset": 0,
  "total": 37
}
```

### GET /history/{id}
- `200` → same shape as a single item above.
- `404` → id not found (standard error shape).

---

## 5. Error response shape (consistent everywhere)
```json
{
  "error": {
    "code": "EXTRACTION_FAILED",
    "message": "Couldn't read the article at that URL. Try pasting the text instead."
  }
}
```
| HTTP | code | When |
|------|------|------|
| 422 | `INVALID_INPUT` | empty/over-length/both-or-neither/invalid URL |
| 422 | `EXTRACTION_FAILED` | URL fetched but no article text found |
| 502 | `LLM_FAILED` | Groq/provider error or timeout |
| 404 | `NOT_FOUND` | history id doesn't exist |
| 500 | `INTERNAL` | unexpected bug |

The `message` is user-friendly (the UI can show it directly); the `code` is stable for programmatic handling.

## 6. Health check
`GET /health` → `200 {"status": "ok"}`. Used by Docker/compose to know the backend is ready before the frontend calls it.

## 7. Why these choices
- **Separate `/summarise` from `/history`** — different concerns; history is read-only.
- **One-of text/url instead of two endpoints** — same business outcome (a summary); keeps the frontend simple.
- **Consistent error envelope** — the frontend has one place to handle errors.
- **`limit`/`offset` pagination** — history grows; never return unbounded lists.
- **No auth in v1** — single-user local (documented assumption); add a token/header in a later phase.
