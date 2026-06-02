# 🎯 24/7 Order Status & Tracking Agent

> **⚠️ Disclaimer:** This is a **personal AI learning project** created for portfolio purposes. This is **not** Target Corporation's official product, use case, or repository. I have no affiliation with Target's engineering or product teams. All Target branding references are used solely for illustrative purposes in a product design exercise. Mock data, personas, and scenarios are entirely fictional.

---

<div align="center">

![Status](https://img.shields.io/badge/status-portfolio%20project-blue)
![Phase](https://img.shields.io/badge/phase-1%20MVP-teal)
![Model](https://img.shields.io/badge/model-Gemini%202.0%20Flash%20Live-orange)
![Built with](https://img.shields.io/badge/built%20with-Google%20AI%20Studio-red)

**A product design & AI engineering case study** — end-to-end PM brief + working conversational agent for retail order tracking, built with Gemini 2.0 Flash Live in Google AI Studio.

[View Product Brief](#-product-brief) · [Try the Prompt](#-getting-started) · [Architecture](#-architecture) · [Metrics](#-success-metrics)

</div>

---

## 📋 Table of Contents

- [About This Project](#-about-this-project)
- [Product Brief](docs/product_brief.md)
- [Goal](docs/product_brief.md#goal)
- [User Ecosystem](docs/product_brief.md#user-ecosystem)
- [Chosen Segment & Pain Points](docs/product_brief.md#chosen-segment--pain-points)
- [Solutions & Prioritization](docs/product_brief.md#solutions--prioritization)
- [Implementation Roadmap](docs/product_brief.md#implementation-roadmap)
- [Success Metrics](docs/product_brief.md#success-metrics)
- [Architecture](docs/architecture.md)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Conversation Flows](#-conversation-flows)
- [What I Learned](#-what-i-learned)

---

## 🧠 About This Project

This project is a **full product design + AI prototype** exercise. It follows the process a senior PM would use to design an AI agent from scratch:

1. Define the goal and business case
2. Map the user ecosystem and choose the highest-impact segment
3. Identify and prioritize pain points
4. Design and prioritize solutions using an Impact × Effort framework
5. Build a phased implementation roadmap
6. Define success metrics (North Star, Supporting, and Do No Harm)
7. Write a production-quality system prompt and test it in Google AI Studio

The output is both a **product brief** (what a PM delivers) and a **working AI agent** (what an engineer builds) — in one repo.

---

## 📌 Product Brief

### Goal

**Eliminate the friction of "where is my order?" for every retail guest — at any time, on any channel — through a conversational AI agent that resolves order queries instantly and proactively.**

In a typical large-scale retail operation, approximately 35% of all inbound customer service contacts are WISMO (Where Is My Order?) queries. These are:
- High-volume and repetitive
- Fully resolvable with the right data
- Currently consuming agent hours that could be redirected to complex, high-value interactions

| Goal Type | Goal | Target |
|---|---|---|
| Guest Experience | Resolve any WISMO query in under 60 seconds | < 60 sec resolution |
| Business | Deflect WISMO contacts from human agents | 60% deflection rate |
| Proactive CX | Notify guests of delays before they ask | Proactive-first model |
| Strategic | Establish benchmark for AI-powered post-purchase CX | Retail CX leadership |

**Out of scope for v1:** Returns & exchanges, payment disputes, product recommendations, in-store availability, Shipt shopper coordination.

---

### User Ecosystem

Seven actors interact with or are affected by this agent:

| Actor | Type | Description | Priority |
|---|---|---|---|
| 🏠 **Busy Parent** | Primary Guest | Orders for the household, 35–45 age group, ~5 orders/month, high anxiety around delivery windows | ⭐ Selected |
| 📱 **Digital Native** | Primary Guest | App-first, 22–34, high frequency, low tolerance for friction | High |
| 🛍️ **Occasional Shopper** | Primary Guest | Phone-first, 50–65, lower frequency, needs plain language | Medium |
| 💎 **Circle Loyalist** | Power User | Multi-fulfillment, all ages, high CLV and CX expectations | High |
| 🎧 **Guest Care Agent** | Internal | Receives AI-escalated cases, needs full context handoff | Internal |
| 📦 **Fulfillment Lead** | Internal | Manages order exceptions at store/DC level | Internal |
| 🚚 **Carrier Partner** | External | Provides real-time tracking data via API | Dependency |

---

### Chosen Segment & Pain Points

**Chosen: The Busy Parent**

This segment represents the highest combination of contact frequency, emotional stakes, and deflection opportunity. They use all fulfillment types (ship-to-home, Drive Up, split shipments) making them the ideal design anchor — solve their experience completely and you solve for Digital Native and Circle Loyalist too.

**All 10 pain points, ranked by Frequency × Impact:**

| # | Pain Point | Frequency | Impact | Status |
|---|---|---|---|---|
| 1 | No proactive delay communication — the "surprise wait" | Very High | Critical | ⭐ **Chosen** |
| 2 | 8–12 minute hold time for a 30-second answer | Very High | High | Addressed by core agent |
| 3 | Broad 6 AM–10 PM delivery window, can't plan the day | High | High | Partially addressed in v1 |
| 4 | Split shipments — "where's the rest of my order?" | High | Medium-High | Addressed in v1 |
| 5 | Marked "delivered" — item never received | Medium | Critical | Addressed via escalation |
| 6 | Confusion across Target's fulfillment types | Medium-High | Medium | Addressed in prompt |
| 7 | Repeating the situation across channels and agents | High | Medium | Addressed via context handoff |
| 8 | No self-serve resolution for delayed/lost orders | Medium | High | Partial v1 |
| 9 | Holiday / Black Friday anxiety with zero communication | Seasonal | Critical | Phase 1 infra |
| 10 | Can't initiate a return from within the tracking flow | Medium | Medium | Phase 4 |

**Chosen Pain Point #1 — The Surprise Wait:**

The guest expects delivery by EOD. No alert arrives. They stay home all day. They discover the delay after 7 PM when they finally call in — frustrated, feeling invisible. This is the highest-volume, highest-emotion contact type and is **entirely preventable** with the right agent design.

---

### Solutions & Prioritization

All solutions mapped using the Impact × Effort framework:

```
HIGH IMPACT
    │
    │  QUICK WINS              STRATEGIC BETS
    │  ─────────────           ──────────────
    │  S1: Proactive SMS/push  S3: App/web AI chatbot (core)
    │  S2: Auto-compensation   S4: Voice IVR AI deflection
    │  S7: Contextual FAQ      S5: Seamless agent handoff
    │                          S6: Predictive delay ML model
    │
    │  FILL-INS                DEPRIORITIZE
    │  ────────                ────────────
    │  S8: Split shipment view S9: WhatsApp channel
    │                          S10: Email response bot
LOW IMPACT
         LOW EFFORT ──────────────────── HIGH EFFORT
```

**Prioritized solution list:**

| ID | Solution | Phase | Effort | Impact |
|---|---|---|---|---|
| S1 | Proactive delay SMS/push notification | 1 | Low | Very High |
| S2 | Auto-compensation on verified 24hr+ delay | 1 | Low–Med | High |
| S3 | App/web conversational AI chatbot (core agent) | 1–2 | High | Very High |
| S4 | Voice IVR AI — deflection on inbound calls | 2 | Very High | Very High |
| S5 | Seamless agent context handoff to human | 2 | Medium | High |
| S6 | Predictive delay alerting (ML model) | 3 | Very High | Very High |
| S7 | Contextual tracking FAQ upgrade | 1 | Low | Medium |
| S8 | Split shipment unified tracking view | 2 | Medium | Medium |
| S9 | WhatsApp conversational channel | Deprioritized | High | Low–Med |
| S10 | Email response bot | Deprioritized | High | Low |

---

### Implementation Roadmap

#### Phase 0 — Discovery & Foundation (Weeks 1–4)
- Audit OMS, carrier APIs, and CDP data readiness
- Define and contract all tool schemas
- 20 guest research interviews with Busy Parent segment
- Establish baseline metrics (WISMO volume, handle time, CSAT, cost per contact)
- Legal & privacy review — PII handling, CCPA compliance

#### Phase 1 — MVP: Proactive Notifications + App Chatbot (Weeks 5–12)
**Delivers: S1, S2, S3 (v1), S7**
- S1: Proactive delay SMS/push — OMS webhook → notification pipeline
- S2: Auto-compensation engine — rule-based Circle credit on 24hr+ delay
- S3: App/web chatbot — session auth, 5 core intents, OMS + carrier tool calls
- S7: Contextual FAQ upgrade on order status page
- Rollout: 5% A/B test → measure containment rate and CSAT

> **Phase 1 Gate:** Containment rate ≥ 40% · CSAT ≥ 3.8 · Zero PII incidents

#### Phase 2 — Scale: Voice IVR + Context Handoff (Weeks 13–22)
**Delivers: S4, S5, S8**
- S4: Replace legacy IVR with conversational voice agent (streaming STT → LLM → TTS)
- S5: Context handoff bundle — full transcript + case summary to Zendesk
- S8: Split shipment unified view across all packages under one order
- Full chatbot rollout to 100% of app + web traffic
- Holiday hardening: load test at 10x baseline (Black Friday ready by week 20)

> **Phase 2 Gate:** Containment rate ≥ 60% · Voice latency p95 < 2s · CSAT ≥ 4.0

#### Phase 3 — Optimize: Predictive Alerting (Weeks 23–36)
**Delivers: S6 + personalization layer**
- S6: ML model trained on carrier history, weather, hub congestion, volume patterns
- Personalized tone by guest tier (Circle Plus vs. first-time guest)
- Real-time 2-hour delivery window narrowing
- Accessibility: WCAG 2.1 AA compliance, Spanish localization

#### Phase 4 — Expand: Adjacent Use Cases (Month 9+)
- Return initiation within the tracking conversation
- Drive Up and Order Pickup status notifications
- Agent API open to voice assistant integrations (Google Assistant, Alexa)

---

### Success Metrics

#### ⭐ North Star Metric

**WISMO Containment Rate** — the percentage of all "Where Is My Order" contacts across all channels that are fully resolved by the AI agent without human escalation.

| Timeframe | Target |
|---|---|
| 6 months | 60% |
| 12 months | 75% |

*Why this metric:* It captures self-serve effectiveness, guest trust, operational efficiency, and cost impact in a single number. Every stakeholder — product, engineering, guest care, finance — can align on it.

#### Supporting Metrics

**Guest Experience**
- Agent CSAT score: ≥ 4.2 / 5.0 for AI-resolved interactions
- Time to resolution: Median < 60 seconds (vs. 8–12 min hold time today)
- Proactive notification open rate: ≥ 55% for delay alerts
- First contact resolution rate: ≥ 85%

**Business Efficiency**
- Cost per WISMO contact: 70% reduction vs. human baseline
- Human agent handle time (escalated): 30% reduction via context handoff
- Peak season capacity: Handle 5x surge without SLA breach
- Agent response latency: p95 < 2 seconds

#### 🚫 Do No Harm Guardrail Metrics

These are non-negotiable. Any adverse movement triggers a rollback review:

| Metric | Threshold | Why |
|---|---|---|
| Target Guest Satisfaction Score | Must not decline from baseline | Protects overall brand trust |
| Escalation abandonment rate | < 5% drop before connection | Guests who escalate need humans |
| App store rating delta | No sustained decline attributable to AI chat | Brand perception |
| Re-contact rate within 24 hours | < 8% | Measures true resolution quality |
| PII exposure incidents | Zero tolerance | Guest safety, legal risk |
| Incorrect ETA delivery rate | < 0.1% | Trust in agent accuracy |
| Auto-compensation false trigger rate | < 0.5% | P&L protection |
| Accessibility compliance | WCAG 2.1 AA at every phase gate | Inclusive design |

**Measurement cadence:**
- Daily: Containment rate, latency, error rates, PII alerts
- Weekly: CSAT, FCR, cost per contact, app store rating
- Monthly: TGSS delta, business case review, re-contact analysis
- Phase gates: Full metric scorecard required before each phase launch

---

## 🏗️ Architecture

### System Overview

The agent is built as a **layered architecture** — each layer has one clear responsibility and hands off to the next with a well-defined contract. No layer does more than its job. This separation is deliberate: it means you can swap the LLM, add a new channel, or replace a backend system without rebuilding everything else.

```
╔══════════════════════════════════════════════════════════════════════╗
║                     LAYER 1 — CUSTOMER CHANNELS                     ║
║         Voice · App Chat · Web Chat · SMS · Email (Phase 2+)        ║
╚══════════════════════════════════╦═══════════════════════════════════╝
                                   ║  Raw input (text / audio / event)
╔══════════════════════════════════╩═══════════════════════════════════╗
║               LAYER 2 — CHANNEL ORCHESTRATION LAYER                 ║
║    Authentication · Input normalisation · Session state · Routing    ║
╚══════════════════════════════════╦═══════════════════════════════════╝
                                   ║  Structured message + session context
╔══════════════════════════════════╩═══════════════════════════════════╗
║                    LAYER 3 — AI AGENT CORE                          ║
║      System prompt · Intent classification · Tool call decisions     ║
║      Response generation · Gemini 2.0 Flash Live (streaming)        ║
╚════╦══════════╦══════════════════╦══════════════════╦═══════════════╝
     ║          ║                  ║                  ║
     ║ Tool calls (function calling — AUTO mode)      ║
     ║          ║                  ║                  ║
╔════╩══╗  ╔════╩══════╗  ╔════════╩══╗  ╔════════════╩══╗
║LAYER 4║  ║  LAYER 4  ║  ║  LAYER 4  ║  ║   LAYER 4     ║
║ Tool  ║  ║   Tool    ║  ║   Tool    ║  ║    Tool       ║
║ get_  ║  ║  get_     ║  ║  get_     ║  ║  escalate_    ║
║orders ║  ║ tracking  ║  ║  status   ║  ║  to_human     ║
╚════╦══╝  ╚════╦══════╝  ╚════╦══════╝  ╚═══════╦═══════╝
     ║          ║              ║                  ║
╔════╩══╗  ╔════╩══════╗  ╔════╩══════╗  ╔════════╩══════╗
║LAYER 5║  ║  LAYER 5  ║  ║  LAYER 5  ║  ║   LAYER 5     ║
║  OMS  ║  ║  Carrier  ║  ║  CDP/CRM  ║  ║  Human Queue  ║
║       ║  ║   APIs    ║  ║           ║  ║  + Helpdesk   ║
╚═══════╝  ╚═══════════╝  ╚═══════════╝  ╚═══════════════╝
                                   ║
╔══════════════════════════════════╩═══════════════════════════════════╗
║              LAYER 6 — PROACTIVE NOTIFICATION ENGINE                ║
║      Webhook listeners · Delay triggers · SMS / Push / Email        ║
╚══════════════════════════════════╦═══════════════════════════════════╝
                                   ║  Events + session logs
╔══════════════════════════════════╩═══════════════════════════════════╗
║                  LAYER 7 — ANALYTICS & OBSERVABILITY                ║
║   Containment rate · CSAT · Latency · Escalation audit · PII alerts ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

### Layer 1 — Customer Channels

**What it is:** The entry points through which guests reach the agent. In Phase 1, this is app chat and web chat. In Phase 2, voice (IVR) is added.

**How it works:**

Each channel produces a different input format and has different latency expectations:

| Channel | Input Format | Latency Budget | Phase |
|---|---|---|---|
| App Chat | Text string | < 2 seconds | Phase 1 |
| Web Chat | Text string | < 2 seconds | Phase 1 |
| Voice / IVR | Audio stream (PCM 16kHz) | < 1.5 seconds (streaming) | Phase 2 |
| SMS | Text string (Twilio webhook) | < 3 seconds | Phase 2 |
| Email | Parsed text from inbound email | < 60 seconds (async) | Phase 3 |

For voice specifically, the audio pipeline looks like:

```
Guest speaks → STT (Speech-to-Text) → text → Agent Core → text response → TTS (Text-to-Speech) → Guest hears
```

Gemini 2.0 Flash Live handles the STT → LLM → TTS pipeline natively in a single bidirectional stream, which is what makes it the right model choice for voice. Alternative models require stitching three separate services together, adding latency and failure points.

**Why it matters:** The channel is where the guest's emotional state is highest and patience is lowest. A guest calling from their phone about a missing package expects to be helped immediately — not transferred, not re-authenticated, not asked to repeat themselves. The architecture must ensure the channel layer adds zero friction and passes the guest context forward completely.

---

### Layer 2 — Channel Orchestration Layer

**What it is:** The middleware that sits between the raw channel input and the AI agent. It does four things: authenticate the guest, normalise the input into a standard format, maintain session state across turns, and route the conversation to the right agent.

**How it works:**

```
Incoming request
      │
      ├─ 1. Authentication
      │      └─ Validate session token from app/web cookie
      │         Extract: customer_id, first_name, loyalty_tier
      │         Inject as session context into every agent message
      │
      ├─ 2. Input normalisation
      │      └─ Voice: run STT, strip filler words ("um", "uh")
      │         SMS: strip carrier prefixes, decode emojis
      │         All channels: trim whitespace, detect language
      │
      ├─ 3. Session state management
      │      └─ Store conversation history in Redis (keyed by session_id)
      │         Append each turn (user + assistant messages) to history
      │         Pass full history to LLM on each turn (LLMs are stateless)
      │         TTL: 30 minutes of inactivity clears the session
      │
      └─ 4. Routing
             └─ Phase 1: All WISMO traffic → Order Status Agent
                Phase 2+: Intent pre-classifier routes to specialist agents
                          (returns agent, payments agent, etc.)
```

**The session state problem:** LLMs have no memory between API calls. Every time the guest sends a message, the model sees it as the first message ever — unless you pass the full conversation history. The orchestration layer is responsible for assembling this history on every turn. Without it, the agent asks "What's your order number?" every single message.

**Why it matters:** This layer is invisible to the guest but critical to the experience. It's the difference between an agent that feels like a coherent conversation and one that feels like a broken phone menu that forgets what you said two seconds ago. It also ensures that authentication happens once, at the edge — the agent layer never has to handle login, tokens, or identity verification.

---

### Layer 3 — AI Agent Core

**What it is:** The brain of the system. This is where the LLM lives — Gemini 2.0 Flash Live in production — along with the system prompt that defines the agent's identity, flows, tone rules, tool-calling behaviour, and guardrails.

**How it works:**

On every turn, the agent receives a structured message bundle:

```json
{
  "system": "[Full system prompt — 2,400 tokens]",
  "session_context": {
    "customer_id": "C-001",
    "first_name": "Sarah",
    "loyalty_tier": "member"
  },
  "conversation_history": [
    {"role": "user", "content": "Where's my order?"},
    {"role": "assistant", "content": "Let me look that up for you..."},
    {"role": "tool", "name": "get_customer_orders", "result": {...}}
  ],
  "current_message": "It was supposed to arrive yesterday"
}
```

The model then decides one of three actions:

1. **Respond directly** — if the answer is already in context (e.g. guest asks a follow-up about an order already loaded)
2. **Call a tool** — if it needs fresh data (e.g. guest asks about a new order, or needs live tracking)
3. **Escalate** — if the situation meets any escalation threshold defined in the system prompt

**Why Gemini 2.0 Flash Live specifically:**

| Requirement | Why Flash Live |
|---|---|
| Real-time streaming responses | Native bidirectional streaming — responses start appearing before generation is complete |
| Voice support | Native audio I/O — no external STT/TTS services needed in Phase 2 |
| Function calling | Reliable tool-use with AUTO mode — model decides when to call, what to call |
| Low latency | Flash-class model, optimised for speed over raw capability |
| Cost at scale | Flash is significantly cheaper per token than Gemini Pro — critical for millions of WISMO queries |

**Temperature = 0.3 — why this specific value:**

Temperature controls how "creative" the model is with its outputs. For a customer service agent handling transactional data:
- `0.0` — responses become robotic and repetitive. Every "out for delivery" query sounds identical.
- `0.3` — factually grounded but with natural tone variation. The agent sounds like a person, not a form letter.
- `0.7+` — risk of the model "filling in" ETAs it doesn't actually have, or making promises it can't keep.

**Why it matters:** The system prompt is the most important engineering artefact in this entire project. It defines not just what the agent says, but what it refuses to say, when it escalates, how it handles failure, and what tone it uses for a frustrated Gold-tier member vs. a first-time guest. A poor system prompt produces an agent that apologises robotically, invents delivery dates, and fails to escalate when it should. The prompt in this repo is designed to prevent all three.

---

### Layer 4 — Tool / Function Layer

**What it is:** The bridge between the LLM and the real-world backend systems. The agent never calls an API directly — it calls a tool, which is a wrapper function that handles authentication, input validation, error handling, retries, and response formatting.

**How it works — the function calling loop:**

```
Agent decides it needs order data
          │
          ▼
Agent emits a "tool call" in its response:
{
  "tool_call": {
    "name": "get_order_status",
    "parameters": {
      "order_id": "ORD-20490",
      "customer_id": "C-001"
    }
  }
}
          │
          ▼
Orchestration layer intercepts the tool call
Calls the tool wrapper function get_order_status()
          │
          ▼
Tool wrapper:
  1. Validates customer_id matches session (security check)
  2. Calls internal OMS API with service-level credentials
  3. Handles timeout (retry once, then return error object)
  4. Formats the raw OMS response into a clean JSON structure
  5. Returns result to the orchestration layer
          │
          ▼
Result is appended to conversation history as a "tool" turn
Agent sees the result and generates the guest-facing response
```

**The four tools in detail:**

**`get_customer_orders`**
- Called when: Guest says "my order" without specifying which one
- What it does: Fetches the last 5–10 orders from the OMS for this customer_id
- Critical parameter: `customer_id` must match the authenticated session — this prevents one guest from being shown another guest's orders
- Why it matters: Most guests don't know their order ID. This tool lets the agent find the right order from natural language ("the shoes I ordered last week") without requiring the guest to look up a number

**`get_order_status`**
- Called when: Agent has an order_id and needs current status, line items, and shipment structure
- What it does: Queries the OMS for the full order record — status, items, fulfillment type, split shipment groups, delay history, cancellation eligibility
- Why it matters: This is the source of truth for what actually happened with an order. The carrier APIs only know about shipping — the OMS knows about everything upstream (picking, packing, payment, cancellation). You always call this before calling get_tracking_info.

**`get_tracking_info`**
- Called when: Order status is `in_transit`, `out_for_delivery`, or `delivered`
- What it does: Calls the carrier's tracking API (FedEx, UPS, USPS, OnTrac) and returns the full milestone history, current location, ETA, delay flag, and delay reason
- Failure handling: Carrier APIs fail more often than internal systems (3–5% error rate in production). The tool wrapper catches these failures and returns a structured error object — the agent then tells the guest the tracking system is temporarily unavailable rather than guessing or silently failing
- Why it matters: This is the data guests actually care about most — where is the physical package right now. Without this, the agent can only say "it's shipped" with no actionable detail. With it, the agent can say "it's in Memphis, delayed by weather, arriving Thursday."

**`escalate_to_human`**
- Called when: Any of the 6 escalation conditions are met (see system prompt)
- What it does: Creates a priority case in Zendesk/Salesforce, passes the full conversation transcript, case summary, sentiment level, and order details, and returns a case_id and estimated wait time
- The context bundle it sends: conversation transcript, all order_ids discussed, detected sentiment level, whether compensation was already offered, one-line case summary written by the agent
- Why it matters: This tool closes the loop between the AI and human agent layers. The human agent receives a case that is pre-briefed — they know what the guest ordered, what went wrong, what the AI already tried, and what the guest wants. The guest never has to repeat themselves. This single feature has an outsized impact on CSAT for escalated cases.

**Why tools instead of direct API calls:**

The LLM is not a trustworthy API client. It cannot handle OAuth, retry logic, rate limits, or error parsing. Tools give the agent a clean, safe interface to the real world — the agent describes what it needs, and the tool handles the complexity of getting it. This also means you can change the underlying API (swap OMS providers, add a new carrier) without changing the agent's behaviour at all.

---

### Layer 5 — Backend Systems

**What it is:** The actual data stores and third-party services that hold the ground truth about orders, shipments, and customer profiles.

**Order Management System (OMS)**

The OMS is the system of record for everything that happens to an order from the moment a guest clicks "Place Order" to the moment a return is processed. For a retailer like Target, this is typically a combination of:
- A proprietary order management platform (or SAP OMS, Manhattan Associates, etc.)
- A fulfillment management system that coordinates between distribution centres and stores
- A store order management system for Drive Up and Order Pickup

The OMS API is called by the `get_order_status` and `get_customer_orders` tools. It is an internal API, authenticated at the service level with a service account credential — the guest's authentication never touches the OMS directly.

**Carrier APIs (FedEx, UPS, USPS, OnTrac)**

These are external REST APIs provided by the shipping carriers. They return tracking milestone events — the sequence of scans a package goes through from pickup at the fulfilment centre to delivery at the guest's door.

Key design consideration: Carrier APIs are the least reliable component in the system. They have higher error rates, slower response times, and less predictable data quality than internal APIs. The tool wrapper adds:
- A 2-second timeout (carrier APIs can be slow)
- One automatic retry on timeout
- Structured error responses so the agent handles failure gracefully
- A `tracking_watch` event log so the proactive notification engine can retry later

**CDP / CRM (Customer Data Platform)**

The CDP holds the guest's full profile — loyalty tier, purchase history, contact preferences, opt-in/opt-out status for SMS and push notifications, and language preference. The orchestration layer queries the CDP once at session start to build the session context that is injected into every agent message.

Why this matters: The agent's ability to personalise ("As a Circle Plus member, Sarah..."), offer the right compensation threshold, and send notifications to the right channel all depend on having accurate guest profile data. Without CDP integration, the agent is generic and transactional. With it, it feels like talking to someone who actually knows you.

**Human Agent Queue (Zendesk / Salesforce / Freshdesk)**

The helpdesk system where human agents manage their case queue. When `escalate_to_human` is called, the tool creates a new case with "priority: high" and populates all the context fields. The human agent sees the case appear in their queue, reads the one-line summary, and picks up exactly where the AI left off.

The integration also enables the human agent to push updates back to the guest's chat session — so the channel feels continuous even after handoff.

---

### Layer 6 — Proactive Notification Engine

**What it is:** A separate event-driven system that monitors order and carrier events and pushes notifications to guests before they have to ask. This is arguably the highest-ROI component in the entire architecture — it prevents WISMO contacts from happening in the first place.

**How it works:**

```
OMS emits event: "ORD-20490 status changed to DELAYED"
          │
          ▼
Notification Engine receives webhook
Checks guest's CDP profile:
  - SMS opt-in? YES → send SMS
  - Push opt-in? YES → send push notification
  - Compensation threshold met? (delay > 24hr) → trigger credit
          │
          ▼
Composes personalised message:
  "Hi Sarah — your Nike Air Zoom Pegasus was expected today
   but is delayed due to weather. New ETA: Thursday Jun 5.
   We've added a $5 credit to your Target Circle account.
   [Track your order →]"
          │
          ▼
Sends via Twilio (SMS) or Firebase (push)
Logs notification event: sent_at, channel, content
```

**Events the engine listens for:**

| Event | Notification | Timing |
|---|---|---|
| Status → `delayed` | Delay alert with new ETA + reason | Immediately on event |
| Status → `out_for_delivery` | "Your order is out for delivery today" | Immediately |
| Status → `delivered` | "Your order has been delivered" | Immediately |
| Delivery window narrowed | "Your order will arrive between 2–4 PM" | When carrier provides window |
| Delay > 24 hours | Compensation credit notification | 24hr threshold crossed |
| `order_ready` (Drive Up/Pickup) | "Your order is ready for pickup" | Immediately |

**Why it matters:** Every notification this engine sends is a WISMO contact that doesn't happen. If the engine sends 1 million delay alerts per month and 40% of those guests would have called without the notification, that's 400,000 fewer calls — at roughly $8 per human-handled call, that's $3.2M in monthly cost avoidance from this one component. The notification engine is cheap to build and has the fastest payback of anything in this architecture.

---

### Layer 7 — Analytics & Observability

**What it is:** The telemetry layer that captures every meaningful event in the system — conversation outcomes, tool call latencies, model responses, escalation reasons, notification delivery rates — and makes them queryable for product, engineering, and operations teams.

**What is tracked:**

**Conversation-level events:**
- Session start / end
- Each user turn (anonymised text + intent classification)
- Each tool call: which tool, latency, success/failure
- Agent response: length, sentiment, confidence signal
- Session outcome: `resolved_by_agent` | `escalated_to_human` | `abandoned`
- Post-session CSAT (if guest completes survey)

**System health metrics:**
- Agent response latency (p50, p95, p99) — target: p95 < 2 seconds
- Tool call success rate per tool and per downstream API
- Carrier API error rate by carrier
- Escalation rate by reason code
- Session abandonment rate (guest stops responding)

**PII protection:**
- Guest message text is anonymised before logging (PII redaction pipeline strips names, addresses, card fragments)
- Raw conversation transcripts are stored encrypted, accessible only to authorised roles
- PII access is logged separately for compliance audit

**Alerting:**
- Containment rate drops below 50% → PagerDuty alert
- Carrier API error rate > 10% for any carrier → Engineering alert
- Escalation rate spikes > 2x baseline → Product alert
- Any PII exposure detected → Immediate escalation + rollback trigger

**Why it matters:** Without observability, you are flying blind. You cannot know whether the agent is actually resolving issues, which types of queries fail most often, whether the Delay Protocol is triggering correctly, or whether a carrier API degradation is causing a wave of incorrect "tracking unavailable" responses. The analytics layer is what turns a prototype into a product — it is the feedback loop that enables continuous improvement of every other layer.

---

### Key Design Decisions — The "Why" Behind Each Choice

| Decision | What We Chose | Why Not the Alternative |
|---|---|---|
| **Authentication model** | Pre-authenticate in orchestration layer, inject `customer_id` as trusted context | Authenticating inside the agent prompt creates a surface for prompt injection and is slower |
| **Tool calling mode** | `AUTO` — model decides when to call tools | `ANY` forces a tool call on every turn, adding latency and cost to conversational turns that don't need data; `NONE` removes all data access |
| **Session state** | Redis with 30-minute TTL, full history on every turn | Database persistence is too slow for < 2s latency targets; no history makes the agent amnesiac |
| **Carrier API failure** | Return structured error, tell guest explicitly, log tracking_watch | Silently retrying adds latency; guessing an ETA destroys trust if wrong |
| **Escalation context** | Full context bundle pushed to helpdesk before human joins | Making the human ask the guest to repeat themselves is the single biggest CSAT killer in hybrid AI/human flows |
| **Temperature** | 0.3 | Low enough to prevent ETA fabrication; high enough for natural tone variation across conversation types |
| **One tool per concern** | 4 separate tools with precise descriptions | Fewer, broader tools make it harder for the model to decide which to call; more specific tools produce more reliable tool-calling behaviour |

---

## 🚀 Getting Started

### Prerequisites
- A [Google AI Studio](https://aistudio.google.com) account (free)
- Basic understanding of system prompts and function calling

### Step 1 — Set up AI Studio

1. Go to [aistudio.google.com](https://aistudio.google.com) and open a new **Stream Realtime** project
2. Select model: **Gemini 2.0 Flash Live**
3. Set **Generation config:**
   - Temperature: `0.3`
   - Max output tokens: `512`
   - Top-P: `0.9`
4. Enable **Function calling** (set mode to `AUTO`)

### Step 2 — Load the system prompt

Copy the contents of [`prompts/system_instructions_v1.txt`](prompts/system_instructions_v1.txt) and paste into the **System instructions** field in AI Studio.

### Step 3 — Add tool definitions

Copy the contents of [`tools/tool_definitions.json`](tools/tool_definitions.json) and paste into the **Tools** panel in AI Studio.

### Step 4 — Inject session context

Before your first user message, add this as a system message to simulate an authenticated guest:

```
Session context: customer_id=C-001, first_name=Sarah, circle_tier=circle, locale=en-US, channel=app_chat
```

### Step 5 — Run mock tool responses

When the agent calls a tool, AI Studio will pause and ask for a function response. Use the mock responses in [`tests/mock_responses.json`](tests/mock_responses.json) to simulate the backend.

### Step 6 — Run the test suite

Work through each scenario in [`tests/test_scenarios.md`](tests/test_scenarios.md) to validate agent behavior before sharing with stakeholders.

---

## 📁 Project Structure

```
target-order-agent/
│
├── README.md                          ← This file (full PM brief + setup guide)
│
├── prompts/
│   └── system_instructions_v1.txt    ← Full system prompt for Google AI Studio
│
├── tools/
│   └── tool_definitions.json         ← 4 tool schemas (OMS, carrier, escalation)
│
├── tests/
│   ├── test_scenarios.md             ← 9 QA test cases with expected behavior
│   └── mock_responses.json           ← Sample API responses for AI Studio testing
│
├── docs/
│   ├── product_brief.md              ← Standalone PM brief (goals → metrics)
│   ├── architecture.md               ← Detailed architecture + data flow
│   ├── conversation_flows.md         ← All 5 flows with decision trees
│   └── impact_effort_matrix.md       ← Solutions prioritization with rationale
│
└── src/
    └── README.md                     ← Notes on production implementation path
```

---

## 💬 Conversation Flows

The agent handles 5 core flows in v1:

| Flow | Trigger | Resolution |
|---|---|---|
| **Flow 1: WISMO** | "Where is my order?" | Fetches order + tracking, presents in plain English |
| **Flow 2: Delay** | Order past ETA | Empathy + new ETA + reason + notification opt-in |
| **Flow 3: Split shipment** | "Where's the rest?" | Lists each package separately with individual ETAs |
| **Flow 4: Not received** | "Says delivered but I didn't get it" | 3-step check list → escalation after 24hrs |
| **Flow 5: Drive Up / Pickup** | "Is my pickup ready?" | Status + pickup code + hold period reminder |

See [`docs/conversation_flows.md`](docs/conversation_flows.md) for full decision trees.

---

## 📚 What I Learned

This project taught me several things that don't show up in product management theory:

**On AI agent design:**
- The system prompt is a product spec, not just instructions. Every edge case you don't document becomes a bug in production.
- Temperature 0.3 is a principled choice for transactional agents — not a default. Too low removes natural tone variation; too high risks fabricating ETAs.
- Tool calling mode `AUTO` is correct here, not `ANY`. If the model calls tools on every turn, it becomes slow and expensive without adding value.
- "Do not say `I apologize for the inconvenience`" is one of the highest-ROI lines in any customer service prompt.

**On PM process:**
- Choosing one pain point forces real prioritization. Most PM exercises let you solve everything. Committing to pain point #1 and designing specifically around it produced a sharper solution than addressing the full list.
- The North Star metric needs to be un-gameable. CSAT alone can be inflated by compensation; containment rate cannot — you either resolved it or you didn't.
- "Do No Harm" metrics are the PM's conscience. The guardrail on PII exposure being zero-tolerance isn't just legal risk management — it's the metric that keeps the product trustworthy enough to exist.

**On AI Studio:**
- Vibe coding with Google AI Studio (as shown in the reference video) genuinely compresses the prototype-to-demo cycle from weeks to hours for non-engineers. For PMs, this is a capability shift.
- Mock tool responses in AI Studio let you test every branch of the agent's logic before writing a single line of backend code. Ship the prompt first, then the API.

---

## 📄 License

This project is released under the MIT License for learning and portfolio purposes.

---

## ⚠️ Final Disclaimer

This repository is a **personal portfolio project** created to demonstrate AI product design and prompt engineering skills. It is:

- ❌ Not affiliated with Target Corporation
- ❌ Not an official Target product, feature, or internal tool
- ❌ Not built using any Target internal data, systems, or APIs
- ✅ A fictional product design exercise using Target as a hypothetical retail context
- ✅ Built entirely with publicly available tools (Google AI Studio, Gemini API)
- ✅ Intended for learning, portfolio demonstration, and skill development

All personas, data, metrics, and scenarios in this project are **entirely fictional**.

---

<div align="center">
Built as a product design learning exercise · Not affiliated with Target Corporation
</div>
