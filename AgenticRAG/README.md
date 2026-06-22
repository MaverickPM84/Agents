# Self-RAG vs Agentic RAG — An Enterprise Case Study

A teaching notebook that contrasts **Self-RAG** with **Agentic RAG** using an insurance-claims-processing case study (the fictional *Acme Insurance Corp*). It runs the **same two queries** through both architectures over the **same 6-document corpus** with the **same model** — holding everything constant except the retrieval strategy, which is what makes the comparison meaningful.

> This is a self-contained demo, not a deployable app. There's no package, test suite, or linter — just notebooks you run top to bottom.

## What it demonstrates

| | Self-RAG | Agentic RAG |
|---|---|---|
| Retrieval | Single pass (`k=3`), then relevance-filter | LLM tool loop, up to 10 iterations |
| Tools | Just the retriever | 5 specialized tools |
| Control flow | Linear: retrieve → filter → generate | Iterative: the model decides what to fetch next |

**The core lesson:** on a simple single-fact query both succeed, and Self-RAG is cheaper. On a complex multi-hop query (John Smith, $15k water-damage claim, CA — approvals + deadlines?), Self-RAG produces a fluent answer that *silently* omits the mandatory supervisor approval and the claims-history check, because a single retrieval pass never surfaced those documents. Agentic RAG decomposes the question into targeted tool calls and catches them — and when a retrieval comes back empty, it **surfaces the gap instead of hallucinating over it**.

> Self-RAG's failure is *silent* (the dangerous kind in compliance). Agentic RAG's gaps are *visible and bounded*. Full analysis in **[`TAKEAWAYS.md`](TAKEAWAYS.md)**.

## The five Agentic RAG tools

`retrieve_documents` · `lookup_claims_history` · `get_state_regulations` · `check_approval_requirements` · `calculate_deadline`

Each is a plain Python function exposed to the model via JSON tool schemas; the orchestration loop iterates until the model has enough information to answer.

## Notebooks

| Notebook | What it is |
|---|---|
| **`agentic_rag_v3.ipynb`** | The canonical teaching notebook. No observability. |
| **`agentic_rag_v3_opik.ipynb`** | Same logic, instrumented with **[Opik](https://www.comet.com/docs/opik)** (Comet's open-source LLM observability) so each query shows up as a single trace tree — LLM calls and tool calls nested, with token counts and latency. |

## Provider setup

All chat/LLM calls run through **Groq** via its OpenAI-compatible API, so the OpenAI SDK and `langchain-openai` work as drop-in clients (just a `base_url` + `api_key` change). **Groq has no embeddings endpoint**, so embeddings run **locally** via `sentence-transformers/all-MiniLM-L6-v2` (CPU, ~90 MB downloaded once and cached).

- **Chat model** — set once in cell-4: `GROQ_CHAT_MODEL = "openai/gpt-oss-120b"`. This model does reliable multi-step tool calling, which the Agentic RAG section needs. (`llama-3.3-70b-versatile` fails the tool loop with a `400 tool_use_failed` error — see `CLAUDE.md`.)
- **Embeddings** — local HuggingFace, never Groq.

## Running it

1. Create a `.env` in this directory (copy from `.env.example`):
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
   Get a free key at https://console.groq.com/keys. For the `_opik` variant, also add:
   ```
   OPIK_API_KEY=your_opik_key_here
   OPIK_WORKSPACE=your_comet_username
   ```
   Get an Opik key at https://www.comet.com/api/my/settings. **`OPIK_WORKSPACE` is your Comet username, not a project name.** If a key isn't found, the setup cell falls back to a `getpass` prompt.
2. Run the install cell (cell-3) — installs `openai`, `langchain-openai`, `langchain-huggingface`, `sentence-transformers`, `langchain-chroma`, `chromadb`, `python-dotenv` (and `opik` in the instrumented variant). First run also downloads the embedding model and PyTorch — expect several minutes.
3. Run cells top to bottom. The first cell to hit the Groq API is **cell-10** (Self-RAG); the Agentic RAG query runs at **cell-19**.

`.env` is gitignored and must never be committed. `.env.example` is the safe-to-commit template.

## Observability (the `_opik` variant)

Both RAG paths trace to a single Opik project, `agentic-rag-insurance`:

| Surface | Mechanism |
|---|---|
| Self-RAG (LangChain chains) | `OpikTracer` callback + `@track` |
| Agentic RAG client | `track_openai(client)` — auto-logs every completion |
| Agentic RAG tools | `@track(type="tool")` on each — one span per tool call |
| Agentic RAG orchestration | `@track` on the loop — the whole query is one trace |

**Cost caveat:** Opik auto-computes dollar cost only for known OpenAI/Gemini model IDs. Groq models show token counts and latency (always tracked) but the dollar figure may read as `$0` — expected, not a bug.

See **[`OPIK_NOTEBOOK_GUIDE.md`](OPIK_NOTEBOOK_GUIDE.md)** for a cell-by-cell walkthrough of the instrumented notebook and why observability matters for use cases like this, **[`OPIK_SETUP_GUIDE.md`](OPIK_SETUP_GUIDE.md)** to set it up, and **[`OPIK_TESTING_GUIDE.md`](OPIK_TESTING_GUIDE.md)** to run and verify traces.

## Files

| File | Purpose |
|---|---|
| `agentic_rag_v3.ipynb` | Canonical teaching notebook |
| `agentic_rag_v3_opik.ipynb` | Opik-instrumented variant |
| `TAKEAWAYS.md` | Written analysis of the two architectures |
| `OPIK_NOTEBOOK_GUIDE.md` | Cell-by-cell walkthrough + why observability matters |
| `OPIK_SETUP_GUIDE.md` | How to set up Opik observability |
| `OPIK_TESTING_GUIDE.md` | How to run the instrumented notebook and verify traces |
| `CLAUDE.md` | Detailed guidance (provider split, model choice, conventions) |
| `.env.example` | Template for required secrets |

*All Acme Insurance Corp content is fictional and for illustration only.*
