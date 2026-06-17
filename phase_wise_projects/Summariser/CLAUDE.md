# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

This is a **greenfield project** — no source code exists yet, only planning documents. When implementing, you are building from scratch against the finalised v1 spec in `Summariser.md` (read it first). `../context.md` holds the broader learning roadmap. There is no build/lint/test tooling set up yet; establish it as part of the first implementation.

## Project: Summariser Chatbot

The first project in a learning roadmap (`../context.md`) whose goal is building **complete products**, not just code — with planning, design, development, and deployment.

**Use case:** A user pastes long text **or an article URL** and receives a summary. Intended for meeting notes and long articles.

**Tech stack (v1):**
- Frontend — Streamlit (thin client; calls the API over HTTP)
- API/backend — FastAPI + Pydantic, Python
- LLM framework — LangChain
- Model — Groq `llama-3.3-70b-versatile` (fallback `llama-3.1-8b-instant`); model name in `.env`
- Database — SQLite (summary history, single-user, no login)
- URL extraction — `trafilatura` (pull clean article body from a pasted URL)
- Config — `python-dotenv` + `.env` (Groq API key, model name); `requirements.txt`; `venv`
- Containerisation — Docker + `docker-compose.yml` (backend + frontend as two services); **in v1 scope**
- Tests — `pytest`, **in v1 scope**; cover deterministic parts (extraction, SQLite, validation) and **mock** the LLM call

## Architecture intent

Keep the three layers decoupled so UI, API, and LLM/persistence can evolve independently:
- **Streamlit** is presentation only — it calls the FastAPI `/summarise` endpoint, never LangChain directly.
- **FastAPI** exposes the summarisation endpoint; LangChain chains live behind it. If input is a URL, extract the article body before summarising.
- **SQLite** persists summary history. Keep DB access out of the UI layer.
- The **model provider** sits behind an abstraction. v1 uses Groq; a local **Ollama** model (e.g. `llama3.2:3b`) is a deferred provider that must slot in without touching the UI or API contracts. (Llama 3.3 70B is too heavy for a laptop — local will use a smaller model.)

## Deferred to v2 (build v1 so these slot in cleanly)
- Long inputs exceeding the context window → LangChain **map-reduce** chunking.
- User-selectable summary length/format (v1 hardcodes one default).
- Local Ollama provider.

The user is learning; explain concepts like map-reduce and Ollama when they become relevant rather than assuming familiarity.

## Working agreement (IMPORTANT — how to collaborate on this project)

The user is a beginner who wants to **learn every step** of how an AI engineer builds a product, in the correct sequence. Follow this strictly:
- Work through the planning docs in `docs/` **one at a time, in order** (00 → 01 → ... → 07).
- For each doc: introduce it, let the user read, **explain concepts when asked**, and answer the user's **Open Questions** which they write inside that same doc file.
- **Do NOT move to the next document until the user gives an explicit go-ahead.** No racing ahead.
- **No code is written until all planning docs are reviewed and approved by the user.**
- Teach, don't just produce: explain *what* each step is and *why* it comes when it does.
- Docs `docs/01`–`docs/04` were drafted early and are **unreviewed drafts**; revisit each with the user when reached. Docs `05`–`07` are written when reached so they reflect any decisions changed along the way.

## Roadmap context

This Summariser is project 1 of a planned series of LLM chatbots (Summariser → Content Generator → Customer Support → Research Assistant → Code Generator), followed by agent-based systems and full-stack applications. Favor patterns and structure that generalize to the later projects rather than one-off solutions.
