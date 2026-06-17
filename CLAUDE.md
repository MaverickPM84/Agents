# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository nature

This is an **AI Agents portfolio monorepo** containing independent, self-contained agent projects. There is no shared build, no top-level package, and no cross-project imports. Each subdirectory is its own project with its own tooling and README. Treat them separately — work inside the relevant subdirectory rather than the repo root.

Two projects exist today:

| Project | Type | What it is |
|---|---|---|
| `build-ai-agent-google-adk/` | Runnable Python code | A multi-agent blog writer built on Google's Agent Development Kit (ADK) |
| `order-tracking-agent/` | Design artifacts only (no code) | A PM case study: system prompt + tool schemas + test scenarios meant to be pasted into Google AI Studio |

## `build-ai-agent-google-adk/` — Google ADK blogger

### Commands
All commands run from inside `build-ai-agent-google-adk/`:
```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
adk web                                               # launches the ADK web UI (~http://127.0.0.1:8000)
```
Requires a `.env` in this directory with `MODEL=...` and `GOOGLE_API_KEY=...` (Google AI Studio key). There is no test suite or linter configured.

### Architecture
The runnable agent is `blogger/` (the `temp_agent/` directory is a throwaway scaffold — a bare single-agent example, not part of the blogger). ADK discovers an agent package by importing it and reading the module-level `root_agent`, so the package's `__init__.py` and a `root_agent` symbol in `agent.py` are the required entry points.

`blogger/agent.py` composes a **hierarchy of agents**, not a single LLM call:
- **Two worker `Agent`s** — `BlogPlanner` (topic → Markdown outline) and `BlogWriter` (outline → article). Each writes its result into shared session **state** via `output_key` (`blog_outline`, `blog_post`). Downstream agents read prior outputs by referencing those state keys in their instructions.
- **Two validator `Agent` subclasses** — `OutlineValidationChecker` / `BlogPostValidationChecker` inspect the state key and emit exactly `"ok"` or `"retry"`.
- **Two `LoopAgent`s** — `RobustBlogPlanner` / `RobustBlogWriter` pair each worker with its validator and re-run up to `max_iterations=3` until validation passes. This is the self-correction mechanism.
- **Root `Agent` (`Blogger`)** — exposes the two `LoopAgent`s as callable tools via `agent_tool.AgentTool`, then orchestrates plan → write → suggest-titles through its instruction.

The key pattern to preserve when editing: **state keys are the contract between agents.** An agent's `output_key` is how the next agent receives its input; changing one without updating the referencing instruction silently breaks the chain.

## `order-tracking-agent/` — AI Studio design case study

This project contains **no executable code** — it is a product-design deliverable. The "agent" is the system prompt plus tool schemas, run manually in Google AI Studio (Gemini 2.0 Flash Live), not from this repo. Key files:
- `prompts/system_instructions_v1.txt` — the actual agent behavior (treated as the product spec)
- `tools/tool_definitions.json` — function-calling schemas
- `tests/test_scenarios.md` + `tests/mock_responses.json` — QA cases and mock backend responses to paste in when the model calls a tool
- `docs/` — product brief, architecture, conversation flows, prioritization matrix

To "run" or test it, follow the step-by-step setup in `order-tracking-agent/README.md` (configure AI Studio, paste the prompt and tools, inject session context, work through scenarios). All Target branding is fictional/illustrative; this is not affiliated with Target.

## Secrets

`.env` files are gitignored and must never be committed. A real Google API key was previously committed and force-purged from history; if you touch env handling, keep keys out of tracked files.
