# Opik Observability Setup Guide

This guide describes how I will add **Opik** (Comet's open-source LLM observability platform) tracing to **`agentic_rag_v3_opik.ipynb`** — the copy of the original notebook. The original `agentic_rag_v3.ipynb` will be left untouched.

> **Please review this plan. I will not edit the notebook until you give the go-ahead.**

---

## 0. What we're instrumenting & why

The notebook makes LLM calls through **two different client surfaces**, both pointed at Groq's OpenAI-compatible API. Opik has a distinct integration path for each:

| Section | Cell(s) | Client used | Opik mechanism |
|---|---|---|---|
| Self-RAG | cell-8 | `ChatOpenAI` (langchain-openai) | **`OpikTracer` callback** (LangChain integration) |
| Agentic RAG | cell-16 (client), cell-17 (tool loop) | `OpenAI()` (openai SDK) | **`track_openai()`** wrapper |
| Orchestration fns | cell-8 `SelfRAG.query`, cell-17 `agentic_rag_query` | — | **`@opik.track`** decorator (groups child LLM/tool spans into one trace) |

The goal: every Self-RAG run and every Agentic RAG run shows up in the Opik UI as a single trace, with the individual LLM calls and tool calls nested underneath as spans (token counts, latency, inputs/outputs, and the tool-call chain all visible).

---

## 1. Prerequisites (you do this once, outside the notebook)

1. **Create a free Opik account** at https://www.comet.com/signup (Opik Cloud). Self-hosting is also possible but cloud is simplest for a demo.
2. **Get your API key** from https://www.comet.com/api/my/settings — this is a Comet/Opik key (different from your Groq key).
3. **Note your workspace name** (defaults to your username; shown in the Comet UI).

These will be added to the existing `.env` file in `AgenticRAG/` (which is already gitignored — keys stay out of git):
```
GROQ_API_KEY=gsk_your_key_here          # already there
OPIK_API_KEY=your_opik_key_here         # NEW
OPIK_WORKSPACE=your_workspace_name      # NEW (optional; defaults to "default")
```
I will also update **`.env.example`** with the two new placeholder keys so the template stays accurate.

> **Note on the MCP server (from the doc you linked):** The page you referenced (`/mcp-server`) is about the **Opik MCP server** — a separate tool that lets an AI host (like Claude Code) *read* your traces / log scores from the chat. That's complementary but **not** what instruments the notebook. To actually *produce* traces from the notebook we use the **Opik Python SDK** (covered here). I can set up the MCP server as an optional follow-up step (Section 7) so you can query traces conversationally afterward.

---

## 2. Install the SDK (new dependency)

The notebook's install cell is **cell-3**. I'll add `opik` to it:
```python
%pip install -q openai langchain-openai langchain-huggingface sentence-transformers \
    langchain-chroma langchain-core chromadb python-dotenv opik
```
`opik` pulls in the core SDK plus the LangChain and OpenAI integration helpers.

---

## 3. Configure Opik (edit cell-4)

Cell-4 currently loads env vars and the Groq config. I'll append Opik configuration **after** the existing Groq setup, so all config stays in one place (consistent with the repo convention that cell-4 is the single config cell):

```python
import opik

# Opik observability config. Reads OPIK_API_KEY / OPIK_WORKSPACE from .env.
# If the key is missing, fall back to a prompt (mirrors the GROQ_API_KEY pattern above).
if not os.getenv("OPIK_API_KEY"):
    os.environ["OPIK_API_KEY"] = getpass.getpass("Opik API Key:")

OPIK_PROJECT_NAME = "agentic-rag-insurance"   # all traces group under this project

opik.configure(
    api_key=os.environ["OPIK_API_KEY"],
    workspace=os.getenv("OPIK_WORKSPACE"),    # None -> uses "default"
    # use_local=True would target a self-hosted Opik instead
)
print(f"Opik configured -> project '{OPIK_PROJECT_NAME}'")
```

**Design choices to confirm:**
- Project name `agentic-rag-insurance` — change if you prefer.
- Keeping all config in cell-4 (rather than a new cell) to honor the "config defined once in cell-4" convention in `CLAUDE.md`.

---

## 4. Instrument Self-RAG (edit cell-8)

The Self-RAG path uses `ChatOpenAI` + LangChain LCEL chains (`prompt | llm | parser`). The clean way to trace LangChain is the **`OpikTracer` callback**, passed at invoke time.

Changes to cell-8:
1. Import the tracer and the decorator:
   ```python
   from opik import track
   from opik.integrations.langchain import OpikTracer
   ```
2. Create one tracer in `SelfRAG.__init__`:
   ```python
   self.opik_tracer = OpikTracer(tags=["self-rag"])
   ```
3. Pass it to each `chain.invoke(...)` via config (two call sites — the relevance check and the generation step):
   ```python
   result = chain.invoke(
       {"query": query, "document": doc.page_content[:500]},
       config={"callbacks": [self.opik_tracer]},
   )
   ...
   answer = chain.invoke(
       {"context": context, "query": query},
       config={"callbacks": [self.opik_tracer]},
   )
   ```
4. Decorate the orchestration method so all the per-doc relevance calls + the final generation roll up into **one** trace per query:
   ```python
   @track(project_name=OPIK_PROJECT_NAME)
   def query(self, query: str) -> dict:
       ...
   ```

Result: one trace per `self_rag.query(...)`, with each LLM relevance check and the generation as nested spans.

---

## 5. Instrument Agentic RAG (edit cell-16 and cell-17)

The Agentic RAG path uses the **raw `OpenAI()` client**, so we use `track_openai()`.

**cell-16** — wrap the client right after it's created:
```python
from opik.integrations.openai import track_openai

# Point the OpenAI SDK at Groq's OpenAI-compatible endpoint, then wrap for Opik tracing.
client = OpenAI(base_url=GROQ_BASE_URL, api_key=os.environ["GROQ_API_KEY"])
client = track_openai(client, project_name=OPIK_PROJECT_NAME)
```
This auto-logs every `client.chat.completions.create(...)` call in the tool loop — prompts, responses, model, token usage, latency — with no other changes to the loop body.

**cell-17** — decorate the orchestration function so the multi-iteration tool loop becomes a single trace with each LLM turn nested:
```python
from opik import track   # (or rely on the import added in cell-8)

@track(project_name=OPIK_PROJECT_NAME)
def agentic_rag_query(query: str, verbose: bool = True) -> dict:
    ...
```

**Optional (nice-to-have, will confirm with you):** also decorate the five tool functions in cell-16 with `@track(type="tool")` so each tool execution appears as its own span with its inputs/outputs:
```python
@track(type="tool", project_name=OPIK_PROJECT_NAME)
def lookup_claims_history(name: str) -> str:
    ...
```
This makes the tool-call chain (retrieve → claims history → approval → regulations → deadline) fully visible in the trace tree. I'll include this only if you want it — it touches all five functions.

---

## 6. Verify it works

After implementing, the verification path is:
1. Run cells **3 → 4** (install + configure). Cell-4 should print `Opik configured`.
2. Run cell-6 (vector store), cell-8 (Self-RAG), then **cell-10** — this fires the first traced LLM call. Self-RAG trace appears in Opik.
3. Run cells 16–17, then **cell-19** — the Agentic RAG trace with 5 tool calls appears.
4. Open https://www.comet.com/<workspace>/redirect/projects?name=agentic-rag-insurance (the SDK also prints a direct trace URL) and confirm both traces, their spans, token counts, and latency are visible.

> **Cost-tracking caveat to set expectations:** Opik auto-computes **dollar cost** only for known OpenAI/Gemini model IDs. Because we call Groq models (e.g. `openai/gpt-oss-120b`), the dollar figure may show as 0/unknown — but **token counts and latency are always tracked**, which is what matters for this demo.

---

## 7. (Optional) Opik MCP server — the page you linked

Separately from notebook tracing, the MCP server lets you query your traces from Claude Code ("list my Opik projects", "show the last agentic-rag trace"). If you want it, I'll run:
```bash
claude mcp add --transport stdio opik-mcp \
  --env OPIK_API_KEY=<your-key> \
  --env OPIK_WORKSPACE=<your-workspace> \
  -- uvx opik-mcp
```
Requires `uv` installed (`winget install astral-sh.uv` on Windows). This is independent of the notebook changes and can be skipped or done later.

---

## 8. Documentation updates (after implementation)

To keep the repo consistent with its `CLAUDE.md` conventions:
- Update **`AgenticRAG/CLAUDE.md`** to document the Opik integration (new dep, the two integration surfaces, the new env vars, that the `_opik` notebook is the instrumented variant).
- Update **`.env.example`** with `OPIK_API_KEY` / `OPIK_WORKSPACE` placeholders.
- `TAKEAWAYS.md` cites specific cells — I'll check whether cell renumbering occurs (it won't; I'm editing existing cells, not inserting new ones) and leave it untouched unless needed.

---

## Summary of files touched

| File | Change |
|---|---|
| `agentic_rag_v3_opik.ipynb` | **NEW** copy (already created); all instrumentation goes here |
| `agentic_rag_v3.ipynb` | **Untouched** |
| `.env` | Add `OPIK_API_KEY`, `OPIK_WORKSPACE` (you/I, not committed) |
| `.env.example` | Add the two placeholders |
| `AgenticRAG/CLAUDE.md` | Document Opik integration |
| `OPIK_SETUP_GUIDE.md` | This file |

### Cells edited in the notebook
- **cell-3** — add `opik` to pip install
- **cell-4** — add `opik.configure(...)` + project name
- **cell-8** — `OpikTracer` callback + `@track` on `SelfRAG.query`
- **cell-16** — `track_openai()` wrap of the client (+ optional `@track(type="tool")` on the 5 tools)
- **cell-17** — `@track` on `agentic_rag_query`

No new cells are inserted, so existing cell IDs/numbers stay stable.
