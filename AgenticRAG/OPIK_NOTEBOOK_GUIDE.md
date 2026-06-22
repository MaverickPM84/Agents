# Guide — `agentic_rag_v3_opik.ipynb`

A walkthrough of the **Opik-instrumented** notebook: what each part does, how the tracing is wired in, what you should see in the Opik UI, and — most importantly — **why observability matters for agentic RAG in the first place.**

> This is the "understand it" guide. For pure setup steps see [`OPIK_SETUP_GUIDE.md`](OPIK_SETUP_GUIDE.md); for a run-and-verify checklist see [`OPIK_TESTING_GUIDE.md`](OPIK_TESTING_GUIDE.md); for the architecture analysis see [`TAKEAWAYS.md`](TAKEAWAYS.md).

---

## 1. Why observability at all? (read this first)

The notebook itself proves the case. Run the complex insurance query through plain Self-RAG and you get a **fluent, confident, well-cited answer that is silently wrong** — it omits the mandatory supervisor approval and ignores the policyholder's claims history (cell-13 scores exactly what it missed). Nothing in the output signals the gap. That is the defining risk of LLM systems: **failure is invisible at the output layer.**

Agentic RAG makes this risk worse before it makes it better. Instead of one LLM call you now have a *loop* — the model decides which of 5 tools to call, in what order, how many times, and when to stop. When the answer is wrong, "the LLM messed up" isn't an answer you can act on. You need to see:

- **Which tools were called, with what arguments, in what order?**
- **What did each tool return** — and did a retrieval come back empty?
- **How many LLM round-trips did it take?** (Each one is latency + tokens + money.)
- **Where did the time and cost actually go?**

Without instrumentation you're staring at a `print()` log and a final string. With it, every query becomes a **trace tree** you can open, expand, and inspect span by span.

### Why this is non-negotiable for use cases *like this one*

This is an **insurance-claims compliance** scenario. Look at the stakes baked into the business case (cell-1): `$2.3M/year` from incorrect decisions, **audit trails required with source citations**, regulatory deadlines with **$10,000-per-violation penalties**. For a domain like this, observability isn't a nice-to-have dashboard — it's load-bearing:

| Need in a compliance / high-stakes domain | What tracing gives you |
|---|---|
| **Auditability** — "prove how this decision was reached" | A persisted trace of every retrieval, tool call, input, and output per query |
| **Silent-failure detection** | You can see a tool returned `"No documents found"` even when the final answer reads confidently |
| **Debugging the loop** | The exact tool sequence and arguments — not a black box |
| **Cost & latency control** | Token counts and per-span latency reveal which tool/turn is expensive |
| **Regression tracking over time** | Traces accumulate in a project, so you can compare runs after a prompt/model change |
| **Evaluation foundation** | Logged inputs/outputs are the raw material for scoring, datasets, and CI evals later |

The same argument generalizes to **any agentic system in claims, legal, medical, or financial workflows** — anywhere a plausible-but-incomplete answer is more dangerous than an obvious error, and where you must be able to explain the machine after the fact.

**Opik** (Comet's open-source LLM observability platform) is the tool used here. The point of the notebook is that adding it is *nearly free*: three small integration surfaces, no rewrite of the RAG logic.

---

## 2. What this notebook is

It runs the **same two queries** through **two architectures** over the **same 6-document insurance corpus** with the **same Groq model** — so the only variable is the retrieval strategy. The `_opik` variant is byte-for-byte the same logic as `agentic_rag_v3.ipynb`, **plus** Opik tracing.

- **Self-RAG** (cells 7–13): single-pass retrieve → relevance-filter → generate.
- **Agentic RAG** (cells 14–22): an LLM tool-calling loop with 5 specialized tools that iterates until it has enough information.

The teaching payoff (full version in `TAKEAWAYS.md`): on a simple lookup both succeed and Self-RAG is cheaper; on a complex multi-hop query Self-RAG fails *silently* while Agentic RAG decomposes the question, calls the right tools, and surfaces gaps instead of hiding them.

---

## 3. Cell-by-cell walkthrough

### Setup (cells 3–6)

| Cell | What it does | Opik relevance |
|---|---|---|
| **3** | `%pip install` — includes `opik` alongside the RAG deps. | Adds the tracing SDK. |
| **4** | Loads `.env`, sets `GROQ_BASE_URL` / `GROQ_CHAT_MODEL`, **and configures Opik**: reads `OPIK_API_KEY` / `OPIK_WORKSPACE`, calls `opik.configure(...)`, sets `OPIK_PROJECT_NAME = "agentic-rag-insurance"`. | **This is the single config cell.** All tracing groups under this project. |
| **5** | Defines `INSURANCE_DOCUMENTS` — 6 docs (auto + home policy, claims guidelines, CA regulations, John Smith's claims history, water-damage procedure). | The knowledge base both paths share. |
| **6** | Builds the Chroma vector store with **local** HuggingFace embeddings (`all-MiniLM-L6-v2`); `retriever` with `k=3`. | Embeddings are local because Groq has no embeddings endpoint — see `CLAUDE.md`. |

> **Important about `OPIK_WORKSPACE`:** it's your **Comet username** (e.g. `preetam-kale`), *not* a project name. A wrong value raises `ConfigurationError: Workspace ... is incorrect`. If you change `.env` after a cell already ran, restart the kernel (plain `load_dotenv()` won't override an env var already set in the process).

### Self-RAG path (cells 7–13) — tracing surface #1

**cell-8** defines the `SelfRAG` class. Two Opik touch-points:

```python
from opik import track
from opik.integrations.langchain import OpikTracer

class SelfRAG:
    def __init__(self, retriever):
        ...
        self.opik_tracer = OpikTracer(tags=["self-rag"])   # <- callback for LangChain chains

    @track(project_name=OPIK_PROJECT_NAME)                  # <- whole query = one trace
    def query(self, query: str) -> dict:
        ...
        result = chain.invoke(
            {...},
            config={"callbacks": [self.opik_tracer]},       # <- nest each chain.invoke() as a span
        )
```

- `@track` wraps the entire `query()` method → one parent trace per query.
- `OpikTracer` passed via `config={"callbacks": [...]}` on every `chain.invoke()` → each relevance check and the final generation become **nested LLM spans** under that trace.
- The `tags=["self-rag"]` lets you filter these traces in the UI.

**cell-10** (simple query) → first real LLM call, first trace sent to Opik. **cell-12** (complex query) → a second Self-RAG trace; **cell-13** is the scoring table showing what it silently missed.

### Agentic RAG path (cells 14–22) — tracing surfaces #2 and #3

**cell-16** wires two more surfaces:

```python
from opik.integrations.openai import track_openai

client = OpenAI(base_url=GROQ_BASE_URL, api_key=os.environ["GROQ_API_KEY"])
client = track_openai(client, project_name=OPIK_PROJECT_NAME)   # surface #2: auto-log every completion

@track(type="tool", project_name=OPIK_PROJECT_NAME)             # surface #3: one span per tool call
def retrieve_documents(query, doc_type=None): ...
@track(type="tool", project_name=OPIK_PROJECT_NAME)
def lookup_claims_history(name): ...
# ...and 3 more tools
```

- `track_openai(client)` wraps the OpenAI SDK client so **every** `chat.completions.create()` is logged (prompt, response, model, token usage, latency) with no change to the loop body. It wraps a **Groq-pointed** client — tracing is provider-agnostic.
- `@track(type="tool")` on each of the 5 tools logs every execution as its own **tool span** (inputs + outputs).

**The 5 tools:**

| Tool | Purpose |
|---|---|
| `retrieve_documents` | Vector search over the knowledge base, optional `doc_type` filter |
| `lookup_claims_history` | Find a policyholder's claims record by name |
| `get_state_regulations` | Pull state-specific regulatory requirements/deadlines |
| `check_approval_requirements` | Map a claim dollar amount → required approval level |
| `calculate_deadline` | Compute a deadline date from today |

**cell-17** decorates the orchestrator:

```python
@track(project_name=OPIK_PROJECT_NAME)
def agentic_rag_query(query, verbose=True) -> dict:
    # up to 10 iterations: model picks tools, we execute them, feed results back
```

`@track` here makes the **whole multi-iteration loop one trace**, with each LLM turn (via `track_openai`) and each tool call (via the `@track` tools) nested underneath — the full tool-call tree in a single view.

**cell-19** runs the complex query. In the executed output you can see the model chain **5 tool calls**: `retrieve_documents` → `lookup_claims_history` → `check_approval_requirements` → `get_state_regulations` → `calculate_deadline`, then synthesize. **cells 20–21** print the final answer and the tool list (display only — no new traces).

### Comparison (cell-22) and the condensed setup (cell-23)

- **cell-22** — the Self-RAG vs Agentic RAG summary table.
- **cell-23** — a second, self-contained setup block with a shorter document set, used independently of the cells above. It re-creates `embeddings`/`retriever`; keep its embedding choice consistent with cell-6. (Not traced — it's plain setup.)

---

## 4. The three integration surfaces at a glance

| # | Surface | Where | Mechanism | Produces |
|---|---|---|---|---|
| 1 | Self-RAG (LangChain LCEL chains) | cell-8 | `OpikTracer` callback + `@track` on `query` | Self-RAG trace with nested LLM spans, tagged `self-rag` |
| 2 | Agentic RAG LLM client | cell-16 | `track_openai(client)` | Auto-logged span for every `chat.completions.create` |
| 3 | Agentic RAG tools + orchestration | cell-16, cell-17 | `@track(type="tool")` per tool + `@track` on the loop | One trace per query, with LLM turns + 5 tool spans nested |

The takeaway: **you instrument the *seams*, not the logic.** A decorator on a function, a callback on a chain, a one-line client wrap. The RAG code is unchanged — which is exactly why adding observability to an existing system is cheap.

---

## 5. Reading the traces in Opik

After cell-10 / cell-19, open your project:
`https://www.comet.com/<your-workspace>/redirect/projects?name=agentic-rag-insurance`

What to look for:

- **Self-RAG traces** (tag `self-rag`) — nested LLM spans: the relevance checks + the final generation.
- **Agentic RAG trace** — one tree containing each LLM turn **and** all 5 tool spans, in call order. Expand `retrieve_documents` to see its arguments and return — this is where you'd catch an empty retrieval that the final answer papered over.
- Every span shows **input/output, latency, and token counts.**

**Cost caveat:** Opik auto-computes a dollar figure only for known OpenAI/Gemini model IDs. Groq models show **tokens + latency always**, but the **$ may read as 0/unknown — that's expected, not a bug.** Use token counts as the cost proxy here.

---

## 6. Optional — query traces from Claude Code (MCP)

The Opik MCP server (`uvx opik-mcp`, registered via `claude mcp add`) lets an AI host **read** your traces conversationally ("list my Opik projects", "show the latest trace in agentic-rag-insurance"). It only reads — it is **not** what instruments the notebook (the SDK above does that). Restart your AI host after registration so the tools load.

---

## 7. The one-line summary

> Agentic RAG turns a single LLM call into a multi-step, model-driven loop — more capable, but a black box when it goes wrong. In compliance-grade domains where answers can be *confidently incomplete*, observability is what converts that black box into an auditable, debuggable, cost-visible trace. Opik delivers it by instrumenting the seams (`@track`, `track_openai`, `OpikTracer`) without touching the RAG logic at all.
