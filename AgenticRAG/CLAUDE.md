# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Part of the AI Agents portfolio monorepo. See the repo-root `CLAUDE.md` for monorepo-wide conventions. This file covers the `AgenticRAG/` project specifically.

## What this project is

A single teaching notebook — `agentic_rag_v3.ipynb` — that contrasts **Self-RAG** with **Agentic RAG** using an insurance-claims-processing case study (the fictional "Acme Insurance Corp"). It is a self-contained demo, not a deployable app: there is no package, test suite, or linter.

The notebook walks through:
1. A business case and a set of in-memory `INSURANCE_DOCUMENTS` (policies, guidelines, regulations, claims history, procedures).
2. **Self-RAG** (`SelfRAG` class) — single-pass retrieve → relevance-filter → generate. Demonstrated succeeding on a simple query and falling short on a complex multi-hop one.
3. **Agentic RAG** (`agentic_rag_query`) — an LLM tool-calling loop with five specialized tools (`retrieve_documents`, `lookup_claims_history`, `get_state_regulations`, `check_approval_requirements`, `calculate_deadline`) that iterates until it has enough information.

`TAKEAWAYS.md` is the written analysis of the two architectures (per-query results, the silent-vs-visible failure distinction, cost trade-offs, when-to-use-which). Keep it in sync with the notebook's cell outputs if those change — it cites specific cells (cell-10, cell-12/13, cell-19, cell-22).

## Provider setup: Groq for chat, local embeddings

This notebook runs **all chat/LLM calls through Groq** via Groq's OpenAI-compatible API. Because the code uses the OpenAI SDK and `langchain-openai`, switching providers is just a `base_url` + `api_key` change — no rewrite of the tool-calling logic.

**Key architectural constraint: Groq has no embeddings endpoint.** Only chat/completions are available. So embeddings run **locally** via `langchain-huggingface` (`sentence-transformers/all-MiniLM-L6-v2`, CPU, ~90 MB downloaded once and cached). Do not reintroduce `OpenAIEmbeddings` pointed at Groq — it returns a 401 (this was the original bug in the notebook).

The split, by cell:
| Concern | Where | Provider |
|---|---|---|
| Env loading, `GROQ_BASE_URL`, `GROQ_CHAT_MODEL` | cell-4 | — |
| Embeddings / vector store (Chroma) | cell-6, cell-23 | **Local** HuggingFace |
| Self-RAG LLM (`ChatOpenAI`) | cell-8 | Groq |
| Agentic RAG client (`OpenAI()`) + tool loop | cell-16, cell-17 | Groq |

Config constants are defined once in **cell-4** and referenced everywhere downstream:
- `GROQ_BASE_URL = "https://api.groq.com/openai/v1"`
- `GROQ_CHAT_MODEL = "openai/gpt-oss-120b"`

cell-23 is a second, condensed setup block (a shorter document set for the comparison section). It re-imports and re-creates `embeddings` / `retriever`, so it must stay consistent with cell-6's embedding choice.

## Running it

1. Create a `.env` in this directory (copy from `.env.example`):
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
   Get a free key at https://console.groq.com/keys. If `GROQ_API_KEY` is not found, cell-4 falls back to a `getpass` prompt.
2. Run the install cell (cell-3) — it installs `openai`, `langchain-openai`, `langchain-huggingface`, `sentence-transformers`, `langchain-chroma`, `chromadb`, `python-dotenv`.
3. Run cells top to bottom. First execution downloads the embedding model once.

`.env` is gitignored and must never be committed. `.env.example` is the safe-to-commit template.

### Environment notes
- The notebook kernel uses the **monorepo-root shared venv** (`agents/.venv`), not a venv inside `AgenticRAG/`. The deps live there, so a system Python won't have them importable.
- That venv runs **Python 3.14**, which is bleeding-edge for `chromadb` / `sentence-transformers`. It works today, but a fresh `pip install` failing on these is the likely culprit if the notebook breaks on import — not a code bug.
- The first cell to actually hit the Groq API is **cell-10** (Self-RAG query). Cell-8 only *constructs* `ChatOpenAI` and makes no network call, so API/key/model errors first surface at cell-10 (Self-RAG) or cell-19 (Agentic RAG), not at setup.

## Changing the Groq model

To switch chat models, edit the single constant in **cell-4** and re-run from there:
```python
GROQ_CHAT_MODEL = "openai/gpt-oss-120b"   # change this one line
```
Both the Self-RAG `ChatOpenAI` (cell-8) and the Agentic RAG tool loop (cell-17) read this constant, so one edit updates the whole notebook. Browse available IDs at https://console.groq.com/docs/models.

### Note on model choice for the Agentic RAG section
The Agentic RAG demo depends on the model chaining several tool calls (claims history → approval check → state regulations → procedure lookup), so reliable multi-step tool calling matters here.

**`llama-3.3-70b-versatile` fails this section.** On the complex Agentic RAG query it emits a malformed tool call and Groq rejects the request with a `400 tool_use_failed` error (`<function=lookup_claims_history,{...}</function>`). The Self-RAG section (cells 8–12) works on it, because that path makes no tool calls — so the error first surfaces when you run the Agentic RAG query (cell-19). Use a model with native, reliable tool calling instead:
```python
GROQ_CHAT_MODEL = "openai/gpt-oss-120b"   # OpenAI-trained, clean structured tool calls
```
`meta-llama/llama-4-scout-17b-16e-instruct` and `qwen/qwen3-32b` also handle the tool loop. (The previously-recommended `moonshotai/kimi-k2-instruct` has been removed from Groq — check the live model list at https://console.groq.com/docs/models if a model ID 404s.) Change only that line in cell-4 and re-run; no other code changes are needed.

## Conventions to preserve when editing

- **Keep the OpenAI-compatible surface.** The whole point is that Groq is a drop-in via `base_url`. Pass `base_url=GROQ_BASE_URL` and `api_key=os.environ["GROQ_API_KEY"]` when constructing `ChatOpenAI` / `OpenAI()`; don't hardcode model names at call sites — use `GROQ_CHAT_MODEL`.
- **Embeddings stay local.** Any new vector-store cell should use `HuggingFaceEmbeddings`, not a Groq-keyed `OpenAIEmbeddings`.
- The five Agentic RAG tools are plain Python functions dispatched through `execute_tool`; their JSON schemas in `tools` must match the function signatures.
