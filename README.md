# AI Agents Portfolio

A collection of AI Agent product design and implementation projects.

## Agents

| Agent | Domain | Status |
|---------|----------|----------|
| [Order Tracking Agent](order-tracking-agent/README.md) | Retail CX | Complete |
| [ADK Blog Writer](build-ai-agent-google-adk/) | Multi-Agent Content | Complete |
| [Self-RAG vs Agentic RAG](AgenticRAG/README.md) | Enterprise Search | Complete |
| Concierge Agent | Customer Support | In Progress |
| Shopping Assistant | eCommerce | Planned |

### Project highlights

- **[Order Tracking Agent](order-tracking-agent/README.md)** — a PM case study (system prompt + tool schemas + test scenarios) for a retail order-tracking assistant, designed to run in Google AI Studio.
- **[ADK Blog Writer](build-ai-agent-google-adk/)** — a multi-agent blog writer on Google's Agent Development Kit, with plan → write → self-correct loops between specialized agents.
- **[Self-RAG vs Agentic RAG](AgenticRAG/README.md)** — a teaching notebook contrasting single-pass Self-RAG with an iterative, tool-calling Agentic RAG over an insurance-claims case study; the `_opik` variant adds full LLM-observability tracing.

## Phase-Wise Projects

A structured learning track ([`phase_wise_projects/`](phase_wise_projects/)) focused on building **complete products** — with planning, design, development, and deployment — not just code. It starts with LLM chatbots and progresses to agent-based systems and full-stack applications. See [`context.md`](phase_wise_projects/context.md) for the full roadmap.

| Phase | Project | Type | Status |
|---|---|---|---|
| 1 | [Summariser Chatbot](phase_wise_projects/Summariser/) | LLM Chatbot | Planning |

**Summariser Chatbot (current):** Paste long text or an article URL and get a summary. Stack — Streamlit (UI) → FastAPI + Pydantic → LangChain (Groq `llama-3.3-70b-versatile`) → SQLite, with `trafilatura` URL extraction, Docker Compose, and `pytest`. See [`Summariser.md`](phase_wise_projects/Summariser/Summariser.md) for the v1 spec.

## Skills Demonstrated

- Product Discovery
- Product Strategy/Design - Goal, User Segmentation, User Pains, Solutions, Implementation Roadmap, Success Metrics
- AI Agent Design
- Prompt Engineering
- RAG
- Tool Calling
- Evaluation Frameworks
- Context Engineering
- MCP
- Agent Observability