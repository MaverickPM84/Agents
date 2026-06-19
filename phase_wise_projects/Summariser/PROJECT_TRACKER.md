# Summariser — Project Tracker

> Single source of truth for project progress. Update statuses as we go.
> **Last updated:** 2026-06-19 (end of session — HLD reviewed & approved; LLD next, review scheduled for tomorrow)

## Status legend
- ✅ **Done** — complete and approved
- 🔄 **In Progress** — actively being worked on
- 🔵 **Drafted** — written but not yet reviewed/approved
- ⬜ **Not Started**
- ⛔ **Blocked** — waiting on something

## Working rule
Planning docs are reviewed **one at a time, in order (00 → 07)**. No doc advances until the user gives explicit go-ahead. **No code is written until all planning docs are reviewed and approved.**

---

## Phase 0 — Spec & Setup

| # | Task | Status | Notes |
|---|------|--------|-------|
| 0.1 | Finalise v1 spec (`Summariser.md`) | ✅ Done | Scope, model, stack locked |
| 0.2 | Answer spec open questions (Pydantic, validation) | ✅ Done | Appended to `Summariser.md` |
| 0.3 | Create project tracker (this file) | ✅ Done | — |

---

## Phase 1 — Planning (review docs in order)

Each doc has three sub-steps: **read/introduce → answer open questions → user approves**.

| # | Doc | Drafted? | Reviewed | Open Qs answered | Approved | Status |
|---|-----|----------|----------|------------------|----------|--------|
| 1.0 | `00_development_process.md` | ✅ | ✅ | ✅ (data-model step) | ✅ | ✅ Done |
| 1.1 | `01_prd.md` (Requirements) | 🔵 | ✅ | ✅ (FR9 latency) | ✅ | ✅ Done |
| 1.2 | `02_high_level_design.md` | 🔵 | ✅ | ✅ (persistence orchestration, backend flow, frontend flow, repository) | ✅ | ✅ Done |
| 1.3 | `03_low_level_design.md` | 🔵 | ⬜ | ⬜ | ⬜ | 🔄 Next (review scheduled for tomorrow) |
| 1.4 | `04_api_design.md` | 🔵 | ⬜ | ⬜ | ⬜ | ⬜ Not Started |
| 1.5 | `05_ui_prototype.md` | ⬜ (write when reached) | ⬜ | ⬜ | ⬜ | ⬜ Not Started |
| 1.6 | `06_testing_plan.md` | ⬜ (write when reached) | ⬜ | ⬜ | ⬜ | ⬜ Not Started |
| 1.7 | `07_implementation_plan.md` | ⬜ (write when reached) | ⬜ | ⬜ | ⬜ | ⬜ Not Started |

**Gate:** All of 1.1–1.7 must be ✅ before any code is written.

---

## Phase 2 — Implementation (build in runnable increments)

> Detailed order comes from `07_implementation_plan.md` once approved. This is the expected shape; refine when 07 is written.

| # | Increment | Status | Notes |
|---|-----------|--------|-------|
| 2.0 | Project scaffold (`venv`, `requirements.txt`, folder structure, `.env` + `.gitignore`) | ⬜ | — |
| 2.1 | LLM provider abstraction + Groq provider | ⬜ | Ollama slots in later |
| 2.2 | LangChain summarise chain (core logic) | ⬜ | — |
| 2.3 | URL extraction with `trafilatura` | ⬜ | — |
| 2.4 | SQLite history (schema + read/write layer) | ⬜ | Data at rest |
| 2.5 | FastAPI `/summarise` endpoint + Pydantic models | ⬜ | Data in transit |
| 2.6 | Streamlit UI (form + result + history view) | ⬜ | Thin client; calls API only |
| 2.7 | Tests (`pytest`) — extraction, SQLite, validation; mock LLM | ⬜ | — |

**Gate:** App runs end-to-end locally and tests pass before Phase 3.

---

## Phase 3 — Containerisation & Deployment

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3.1 | `Dockerfile`(s) for backend + frontend | ⬜ | — |
| 3.2 | `docker-compose.yml` (two services) | ⬜ | Needs Docker Desktop |
| 3.3 | `docker compose up` runs full app | ⬜ | — |
| 3.4 | README (setup + run instructions) | ⬜ | — |

---

## Deferred to v2 (tracked, not scheduled)
- ⬜ Long-input handling via LangChain **map-reduce** chunking
- ⬜ User-selectable summary length/format
- ⬜ Local **Ollama** provider (e.g. `llama3.2:3b`)

---

## Open questions log
| Date | Doc | Question | Status |
|------|-----|----------|--------|
| 2026-06-18 | `Summariser.md` | What are Pydantic models? | ✅ Answered |
| 2026-06-18 | `Summariser.md` | What validation happens in our use case? | ✅ Answered |
| 2026-06-18 | `00_development_process.md` | Where is the data-model design step? | ✅ Answered |
| 2026-06-18 | `01_prd.md` | Show response latency (seconds) in the UI? | ✅ Answered → FR9 added; threaded into 03 LLD + 04 API |
| 2026-06-19 | `02_high_level_design.md` | What is persistence orchestration, why/what does it do? | ✅ Answered → §8 |
| 2026-06-19 | `02_high_level_design.md` | How does the backend service work in this use case? | ✅ Answered → §8 |
| 2026-06-19 | `02_high_level_design.md` | How does the frontend service work in this use case? | ✅ Answered → §8 |
| 2026-06-19 | `02_high_level_design.md` | What does "repository" mean (vs git repo)? | ✅ Answered → §8 |
