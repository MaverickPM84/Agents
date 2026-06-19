# 00 — How an AI Engineer Builds a Product (Process Guide)

> This is the index for the Summariser planning docs. It explains **what each step is, why it exists, and why it comes in this order**. Read this first.

## Why we plan before coding

Beginners often open an editor and start typing. Senior engineers don't — because every later decision depends on earlier ones. If you design the API before you know the requirements, you'll redesign it. If you write code before you design the data model, you'll rewrite it. Planning is cheaper than rebuilding. The goal of planning is to **make the expensive mistakes on paper**, where they cost minutes instead of days.

Open Question - Where is the data model design step in below steps ? 

**Answer:** It doesn't get its own numbered step — it lives inside **Step 3, Low-Level Design (LLD)**. The LLD description ("modules, functions, classes, the folder structure, and the **database schema**") is where the data model is designed.

The ordering logic: **HLD (Step 2)** decides *that* a database exists (the box: "SQLite stores history") but not what's in it; **LLD (Step 3)** zooms in and defines the actual columns (e.g. a `summaries` table with `id`, `created_at`, `source_type`, `source_value`, `summary_text`, `model_used`). You can't design the schema until HLD has established the database exists — so it sits inside LLD.

Subtle point for this project — there are **two kinds of "data model", designed in two docs:**

| "Data model" | What it is | Designed in |
|---|---|---|
| **Persistence model** | SQLite **table schema** — data *at rest* (survives after the request) | 03 LLD |
| **API model** | Pydantic **request/response shapes** — data *in transit* (validated at the API boundary) | 04 API Design |

These are related but deliberately kept separate: the shape you *accept over HTTP* and the shape you *store in the DB* are allowed to differ, so one can change without breaking the other. For this summariser the schema is small (one history table), so folding it into LLD is the proportionate call rather than giving it a standalone doc.

A useful mental model: each document below answers one question, and each question can only be answered once the previous one is.

| # | Document | Question it answers | Depends on |
|---|----------|---------------------|------------|
| 01 | PRD (Requirements) | **What** are we building, for whom, and what does "done" mean? | — |
| 02 | High-Level Design | **Which big components** exist and how do they talk? | 01 |
| 03 | Low-Level Design | **How** is each component built inside (modules, schema)? | 02 |
| 04 | API Design | What is the exact **contract** between frontend and backend? | 02, 03 |
| 05 | UI Prototype | What does the **user** see and do? | 01, 04 |
| 06 | Testing Plan | How do we **prove** it works? | 03, 04 |
| 07 | Implementation Plan | In what **order** do we build it? | all above |

## The steps, explained

### 1. Requirements (PRD — Product Requirements Document)
Before anything, write down *what* the product must do. Split into:
- **Functional requirements** — what the system *does* ("summarise pasted text").
- **Non-functional requirements** — *qualities* it must have (speed, cost, reliability, security).

Without this, you can't tell when you're finished, and "scope creep" (endlessly adding features) takes over. The PRD also defines **out-of-scope** items — saying no is part of design.

### 2. High-Level Design (HLD) / Architecture
Zoom out. Draw the **boxes and arrows**: the frontend, the API, the LLM, the database, and the external services (Groq). This is where you decide the *shape* of the system — here, a 3-layer client/API/data split. You also justify **technology choices** so the reasoning isn't lost.

### 3. Low-Level Design (LLD)
Zoom in. For each box, define the **modules, functions, classes, the folder structure, and the database schema**. This is where the "provider abstraction" (swap Groq ↔ Ollama) becomes a concrete interface. Good LLD makes coding almost mechanical.

### 4. API Design
The API is a **contract**. Once the frontend and backend agree on "POST /summarise takes `{text, url}` and returns `{summary, id}`", the two can be built and tested *independently*. Designing this explicitly (endpoints, request/response shapes, error formats, status codes) prevents integration pain later.

### 5. UI Prototype (Wireframes)
A low-fidelity sketch of each screen and its **states** (empty, loading, success, error). Catching "where does the history go?" on a wireframe is free; catching it after coding is not. We use ASCII wireframes — fast and version-controllable.

### 6. Testing Plan
Decide *how you'll prove correctness* **before** coding, because code written to be tested is structured differently (smaller, pure functions; dependencies injected so they can be mocked). Covers the **test pyramid**, what to test, and how to **mock the LLM** so tests are fast, free, and deterministic.

### 7. Implementation Plan
Finally, the build order — broken into **small, runnable increments**. Each increment ends with something you can actually run and verify, so you're never debugging 2,000 lines at once. Docker and deployment come last, once the app works locally.

## How this maps to the real world
This is a lightweight version of the **Software Development Life Cycle (SDLC)**: Requirements → Design → Implementation → Testing → Deployment → Maintenance. Big teams add more ceremony (tickets, reviews, sign-offs), but the spine is identical. Learning it on a small project is exactly how you scale to large ones.

## Document status
- [x] 00 Process guide (this file)
- [ ] 01 PRD
- [ ] 02 High-Level Design
- [ ] 03 Low-Level Design
- [ ] 04 API Design
- [ ] 05 UI Prototype
- [ ] 06 Testing Plan
- [ ] 07 Implementation Plan
