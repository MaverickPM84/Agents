# Testing Guide — `agentic_rag_v3_opik.ipynb`

Step-by-step instructions to run the Opik-instrumented notebook and confirm traces land in the Opik UI.

> Run **`agentic_rag_v3_opik.ipynb`** (the instrumented copy), not the original `agentic_rag_v3.ipynb`.

---

## 0. Pre-flight checklist (one-time)

Before opening the notebook, confirm:

- [ ] **`.env` exists** in `AgenticRAG/` with three values:
  ```
  GROQ_API_KEY=gsk_...
  OPIK_API_KEY=...
  OPIK_WORKSPACE=AgenticRAG
  ```
- [ ] **Groq key is valid** — free key at https://console.groq.com/keys
- [ ] **Opik key is valid** — from https://www.comet.com/api/my/settings
- [ ] **Kernel = the monorepo shared venv** (`agents/.venv`, Python 3.14). In the notebook's kernel picker, select that interpreter — a system Python won't have the deps. (See `CLAUDE.md` → Environment notes.)

---

## 1. Install dependencies (cell-3)

Run **cell-3**. It installs everything including `opik`.

- ✅ **Expect:** pip output ending without errors. You may see `Note: you may need to restart the kernel to use updated packages.`
- ⚠️ **If `opik` was just installed for the first time:** restart the kernel (Kernel → Restart), then continue from cell-3 again so the new package is importable.
- ❌ **If chromadb / sentence-transformers fail to build:** that's the Python 3.14 bleeding-edge issue noted in `CLAUDE.md`, not a code bug — retry or pin versions.

---

## 2. Load config + configure Opik (cell-4)

Run **cell-4**.

- ✅ **Expect two printed lines:**
  ```
  API Key loaded: ...XXXX
  Opik configured -> project 'agentic-rag-insurance'
  ```
- This is where Opik is initialized. **No LLM call happens yet** — so a bad Groq model/key won't surface here.
- ❌ **`getpass` prompt appears for "Opik API Key:"** → your `.env` `OPIK_API_KEY` wasn't picked up. Check the key name/spelling in `.env` and that `load_dotenv()` ran. You can paste the key into the prompt to proceed.
- ❌ **Opik auth error** → wrong `OPIK_API_KEY` or `OPIK_WORKSPACE`. Verify both at the Comet settings page.

---

## 3. Build the vector store (cell-5, cell-6)

Run **cell-5** (documents) then **cell-6** (embeddings + Chroma).

- ✅ **Expect:** `Created 6 documents` then `Vector store ready with 6 documents`.
- ℹ️ **First run downloads the embedding model** (~90 MB, `all-MiniLM-L6-v2`) once — may take a minute. Runs locally on CPU; no network LLM call.

---

## 4. Self-RAG trace (cell-8 → cell-10)

This is the **first LLM call** and the first trace sent to Opik.

1. Run **cell-8** — defines `SelfRAG` with the `OpikTracer` callback and `@track` decorator. Expect `Self-RAG ready!`.
2. Run **cell-10** (simple query: auto-insurance deductible).

- ✅ **Expect console output:** retrieval → relevance checks (Doc 1 RELEVANT, others NOT) → a generated answer citing the auto policy.
- ✅ **In Opik:** a new trace appears under project **`agentic-rag-insurance`**, tagged `self-rag`, with nested LLM spans (the relevance checks + the final generation).
- ❌ **Auth/model error here** = the first real Groq call failing. Check `GROQ_API_KEY` and that `GROQ_CHAT_MODEL = "openai/gpt-oss-120b"` in cell-4.

**(Optional) cell-12** runs the complex query through Self-RAG (intentionally incomplete answer — that's the teaching point). It produces a second Self-RAG trace.

---

## 5. Agentic RAG trace (cell-16 → cell-17 → cell-19)

1. Run **cell-16** — wraps the OpenAI client with `track_openai` and defines the 5 `@track(type="tool")` tools. Expect `Agentic RAG tools ready!`.
2. Run **cell-17** — defines the `@track`-decorated `agentic_rag_query`. Expect `Agentic RAG query function ready!`.
3. Run **cell-19** — the complex query (John Smith, $15k water-damage claim).

- ✅ **Expect console output:** a chain of ~5 tool calls — `retrieve_documents` → `lookup_claims_history` → `check_approval_requirements` → `get_state_regulations` → `calculate_deadline` → `Final answer after 5 tool calls`.
- ✅ **In Opik:** **one** trace for the whole query, with each LLM turn (via `track_openai`) **and** each tool call (via `@track(type="tool")`) nested as child spans — the full tool-call tree.
- ❌ **`400 tool_use_failed`** → the model can't do clean tool calls. Confirm cell-4 is `openai/gpt-oss-120b` (NOT `llama-3.3-70b-versatile`), then re-run cell-4 and cell-16–19.

Run **cell-20** / **cell-21** to print the final answer and the list of tools used (no new traces; just display).

---

## 6. Verify in the Opik UI

1. Open the **trace URL Opik prints** in the cell output, or go to:
   `https://www.comet.com/<your-workspace>/redirect/projects?name=agentic-rag-insurance`
2. **Confirm you see:**
   - [ ] At least one **Self-RAG** trace (tag `self-rag`) with nested LLM spans.
   - [ ] One **Agentic RAG** trace whose tree contains LLM spans **and** 5 tool spans.
   - [ ] Each span shows **input/output**, **latency**, and **token counts**.
3. **Cost column:** likely shows `$0` / unknown — expected, because Opik only auto-prices known OpenAI/Gemini model IDs, not Groq. Tokens + latency are the meaningful signals here.

---

## 7. (Optional) Query traces via the MCP server

The `opik-mcp` server is registered and connected. In a Claude Code session (you may need to **restart Claude Code** first so its tools load), try:

- *"list my Opik projects"*
- *"show the latest trace in agentic-rag-insurance"*

This reads traces conversationally — independent of the notebook.

---

## Quick run order (happy path)

```
3 → 4 → 5 → 6 → 8 → 10 → [12] → 16 → 17 → 19 → 20 → 21
```
Then open the Opik project URL and confirm both trace types.

## Troubleshooting cheat-sheet

| Symptom | Cell | Fix |
|---|---|---|
| `getpass` asks for Opik key | 4 | `OPIK_API_KEY` missing/misnamed in `.env` |
| Opik auth error | 4 | Wrong key or workspace; check Comet settings |
| `ModuleNotFoundError: opik` | 4 | Re-run cell-3, then restart kernel |
| First LLM call fails (401/404) | 10 | Bad `GROQ_API_KEY` or model ID |
| `400 tool_use_failed` | 19 | Set `GROQ_CHAT_MODEL="openai/gpt-oss-120b"` in cell-4 |
| No traces in UI | — | Wrong workspace; check the project name `agentic-rag-insurance` |
| Cost shows $0 | — | Expected for Groq models — not a bug |
