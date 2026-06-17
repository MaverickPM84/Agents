# 01 — Product Requirements Document (PRD)

> **What** we are building, for whom, and what "done" means. Everything else is designed to satisfy this document.

## 1. Problem statement
People deal with long articles, reports, and meeting notes but lack time to read them fully. They need a fast, reliable way to turn long text (or a web article) into a concise summary they can trust and revisit later.

## 2. Goal (v1)
Ship a working web app where a single user can paste text **or** an article URL, receive a quality summary in seconds, and browse their past summaries.

## 3. Target users & use cases
- **Knowledge worker** pasting meeting notes → wants action-oriented gist.
- **Reader/researcher** pasting a news/blog URL → wants the article's key points without reading it all.
- (v1 is **single-user, local** — no accounts, no multi-tenant concerns yet.)

## 4. User stories
- As a user, I can paste raw text and get a summary.
- As a user, I can paste an article URL and get a summary of that article's content.
- As a user, I can see a clear loading state while it works.
- As a user, I can read a helpful error if the URL fails or the text is empty/too long.
- As a user, I can view a history of my previous summaries and re-open one.

## 5. Functional requirements (what it does)
| ID | Requirement |
|----|-------------|
| FR1 | Accept input as either pasted text OR a URL (exactly one per request). |
| FR2 | For a URL, fetch the page and extract the clean article body before summarising. |
| FR3 | Generate a summary using the configured Groq LLM via LangChain. |
| FR4 | Use one fixed default summary style (concise paragraph(s)) in v1. |
| FR5 | Persist each summary (input meta + output + timestamp) to SQLite. |
| FR6 | List past summaries (most recent first) and allow viewing a single one. |
| FR7 | Validate input (reject empty input, malformed URL, and over-length text). |
| FR8 | Return clear, structured errors the UI can display. |

## 6. Non-functional requirements (qualities it must have)
> These are the "-ilities" senior engineers always check. They shape the design as much as features do.

| Category | Requirement |
|----------|-------------|
| **Performance** | Typical summary returns in a few seconds (bounded by Groq latency). UI must never appear frozen — always show a loading state. |
| **Cost** | Stay within Groq free-tier limits; don't re-summarise identical input unnecessarily (nice-to-have caching later). Tests must **not** call the real LLM. |
| **Reliability** | A failure in URL fetch or the LLM must produce a graceful error, never a crash. |
| **Security** | API key only in `.env`, never in code, logs, or git. Treat pasted URLs as untrusted input. |
| **Usability** | Beginner-simple UI: one input, one button, clear result. |
| **Maintainability** | Layered code; LLM provider swappable; covered by tests. |
| **Portability** | Runs the same on any machine via Docker. |
| **Observability** | Basic logging of requests/errors (so failures are diagnosable). |

## 7. Constraints & assumptions
- Single user, local deployment; no auth in v1.
- v1 input assumed to fit the model's context window (no chunking yet).
- Groq free tier; model is `llama-3.3-70b-versatile` (configurable).
- Internet required (Groq is cloud; URL fetch needs network).

## 8. Out of scope (v1) — explicitly NOT building now
- User accounts / login / multi-user.
- User-selectable summary length & format → **v2**.
- Long-document map-reduce chunking → **v2**.
- Local Ollama model → **later** (abstraction prepared now).
- File uploads (PDF/DOCX), mobile app, cloud deployment.

## 9. Success criteria (definition of done for v1)
1. Pasting text returns a sensible summary.
2. Pasting a valid article URL returns a summary of that article.
3. Invalid input shows a helpful error, not a crash.
4. Summaries appear in a persistent history across restarts.
5. `pytest` suite passes with the LLM mocked.
6. `docker compose up` runs backend + frontend together.

## 10. Risks
| Risk | Mitigation |
|------|------------|
| Groq rate limits / outages | Configurable fallback model; graceful error; retry later. |
| Some URLs won't extract cleanly | Detect empty extraction, return a clear "couldn't read that page" error. |
| LLM output varies / hallucinates | Fixed prompt; v1 summarises only provided text; show source for trust. |
| Beginner overwhelmed by scope | Strict v1 scope; phased implementation plan (doc 07). |
