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
- [Product Brief](#-product-brief)
  - [Goal](#goal)
  - [User Ecosystem](#user-ecosystem)
  - [Chosen Segment & Pain Points](#chosen-segment--pain-points)
  - [Solutions & Prioritization](#solutions--prioritization)
  - [Implementation Roadmap](#implementation-roadmap)
  - [Success Metrics](#success-metrics)
- [Architecture](#-architecture)
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

```
┌─────────────────────────────────────────────────┐
│              Customer Channels                   │
│  Voice │ App Chat │ Web Chat │ SMS │ Email       │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         Channel Orchestration Layer              │
│  Normalises input · Session state · Routing      │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         AI Agent Core (LLM + Tool Use)           │
│  Intent classification · Entity extraction       │
│  Response generation · Gemini 2.0 Flash Live     │
└────────────────────┬────────────────────────────┘
                     │ Tool calls
┌────────────────────▼────────────────────────────┐
│              Tool / Function Layer               │
│  get_order_status  get_tracking_info             │
│  get_customer_orders  escalate_to_human          │
└───┬──────────────┬──────────────┬──────────┬────┘
    │              │              │          │
┌───▼──┐    ┌──────▼──┐   ┌──────▼──┐  ┌───▼────┐
│ OMS  │    │Carrier  │   │ CDP/CRM │  │ Human  │
│      │    │  APIs   │   │         │  │ Queue  │
│Shopif│    │FedEx    │   │Auth +   │  │Zendesk │
│/SAP  │    │UPS/USPS │   │Profile  │  │        │
└──────┘    └─────────┘   └─────────┘  └────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         Proactive Notification Engine            │
│  Delay alerts · Delivery confirmations · SMS     │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│           Analytics + Logging                    │
│  Containment rate · CSAT · Latency · Audit trail │
└─────────────────────────────────────────────────┘
```

**Key design decisions:**
- Agent never calls APIs directly — only calls tool wrappers that handle auth, retries, and formatting
- Session authentication is pre-done by middleware — agent trusts the injected `customer_id`
- If carrier API is unavailable, agent states so clearly and logs a `tracking_watch` event — never guesses
- Escalation always passes a full context bundle so guests never repeat themselves
- Temperature set to 0.3 to keep responses factual; agent cannot fabricate ETAs or tracking events

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