# Architecture — 24/7 Order Status & Tracking Agent

> **⚠️ Disclaimer:** This is a **personal AI learning project** created for portfolio purposes. This is **not** Target Corporation's official product, use case, or repository. I have no affiliation with Target's engineering or product teams. All Target branding references are used solely for illustrative purposes in a product design exercise. Mock data, personas, and scenarios are entirely fictional.

---

## System Overview

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

## Layer 1 — Customer Channels

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

## Layer 2 — Channel Orchestration Layer

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

## Layer 3 — AI Agent Core

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

## Layer 4 — Tool / Function Layer

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

## Layer 5 — Backend Systems

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

## Layer 6 — Proactive Notification Engine

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

## Layer 7 — Analytics & Observability

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

## Key Design Decisions — The "Why" Behind Each Choice

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

*Part of the [24/7 Order Status & Tracking Agent](../README.md) portfolio project · Not affiliated with Target Corporation*
