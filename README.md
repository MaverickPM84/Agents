# AI Agents Portfolio

A collection of AI Agent product design and implementation projects.

## Agents

| Agent | Domain | Status |
|---------|----------|----------|
| [Order Tracking Agent](order-tracking-agent/README.md) | Retail CX | Complete |
| Concierge Agent | Customer Support | In Progress |
| Shopping Assistant | eCommerce | Planned |
| RAG Research Agent | Enterprise Search | Planned |

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