# Self-RAG vs Agentic RAG — Key Takeaways

Derived from `agentic_rag_v3.ipynb`, an insurance-claims case study ("Acme Insurance Corp")
that runs the **same two queries** through both architectures over the **same 6-document
corpus** and the **same model**. Holding everything constant except the retrieval strategy
is what makes the comparison meaningful.

## The experiment design

| | Self-RAG (cell-8) | Agentic RAG (cells 16–17) |
|---|---|---|
| Retrieval | Single pass, `k=3`, then relevance-filter | LLM tool loop, up to 10 iterations |
| Tools | Just the retriever | 5 specialized tools |
| Control flow | Linear: retrieve → filter → generate | Iterative: model decides what to fetch next |

## What the outputs actually show

### Simple query — "What is the deductible for auto insurance?" (cell-10)
- Self-RAG retrieved 3 docs, correctly filtered to **1 relevant**, answered correctly:
  `$500 standard / $1000 high-risk`.
- **Takeaway: for single-fact lookups, Self-RAG is sufficient and cheaper.** The agentic
  machinery would add latency and cost for no benefit.

### Complex query — John Smith, $15k water damage, CA, burst pipe: approvals + deadlines? (cell-12 vs cell-19)

This is where the two diverge. Self-RAG marked **RELEVANT** on all 3 retrieved docs and
produced a fluent, confident answer — but the notebook's own scoring table (cell-13) catches
what it *silently missed*:

| What was needed | Self-RAG | Agentic RAG |
|---|---|---|
| CA deadlines (15/40/30 days) | ✅ | ✅ |
| Water-damage procedure | ✅ | ✅ |
| **$15k → supervisor approval** | ❌ missed | ✅ (`check_approval_requirements`) |
| **Claims history / fraud flag** | ❌ ignored | ✅ (`lookup_claims_history`) |
| Citation quality | ❌ cited home policy spuriously | cleaner |

**Mechanism behind the failure:** Self-RAG retrieves once, with a fixed `k=3`. John Smith's
claims-history doc and the approval guideline simply weren't in the top-3 vector hits for that
query — and a single pass has no way to go back for them. The relevance filter can only judge
what was *already retrieved*; it can't discover what's *missing*.

Agentic RAG (cell-19) solved it by **decomposing the query into separate tool calls**:
`lookup_claims_history` → `check_approval_requirements` → `get_state_regulations` →
`retrieve_documents`. Each sub-question got its own targeted fetch.

## The most important — and most honest — takeaway

The notebook doesn't oversell. In cell-19, the `retrieve_documents` call returned
**"No documents found"** (it filtered on `doc_type="procedure"` against the wrong corpus), and
the final answer admitted *"specific internal procedures … were not located."*

So Agentic RAG didn't score perfectly either — but it **failed differently and better**:
- It **knew what to look for** (decomposed correctly, called the right specialized tools).
- When a retrieval came back empty, it **surfaced the gap** instead of hallucinating over it.

That contrast is the real lesson:
- **Self-RAG's failure was silent** — fluent answer, missing facts, no signal anything was
  wrong. The dangerous kind in a compliance setting.
- **Agentic RAG's gap was visible and bounded.**

## The cost side (cell-22)

| Metric | Self-RAG | Agentic RAG |
|---|---|---|
| Simple query | Success | Success |
| Complex query | Incomplete | Comprehensive |
| Latency | ~2–3 sec | ~8–15 sec |
| Cost | Lower | Higher |
| Tool calls | 1 | 5–8 |

Agentic RAG is **3–5× slower and proportionally more expensive** because each tool call is a
full LLM round-trip.

## Bottom line — when to use which

- **Self-RAG** → single-hop, factual lookups; latency- and cost-sensitive paths. It's not
  "worse," it's *right-sized* for simple queries.
- **Agentic RAG** → multi-hop questions needing information from sources one vector search
  won't co-locate; especially where a **silent omission is costly** (compliance, claims, legal,
  medical). You pay latency and tokens to buy completeness and auditability.

## Two meta-points

1. **The upgrade is a retrieval-strategy change, not a rewrite.** Same documents, same model,
   same OpenAI-compatible client — the difference is letting the LLM *decide and iterate* on
   retrieval rather than doing it once. That is the whole thesis of "agentic."
2. **Scope the conclusions honestly.** This is a 6-document toy corpus, so the absolute numbers
   (latency, tool counts) are illustrative, not benchmarks. The *pattern* — single-pass misses
   multi-hop facts silently, iterative tool-calling catches them — is the transferable insight.
