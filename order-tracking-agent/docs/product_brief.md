# Product Brief — 24/7 Order Status & Tracking Agent

> **⚠️ Disclaimer:** This is a **personal AI learning project** created for portfolio purposes. This is **not** Target Corporation's official product, use case, or repository. I have no affiliation with Target's engineering or product teams. All Target branding references are used solely for illustrative purposes in a product design exercise. Mock data, personas, and scenarios are entirely fictional.

---

## Goal

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

## User Ecosystem

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

## Chosen Segment & Pain Points

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

## Solutions & Prioritization

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

## Implementation Roadmap

### Phase 0 — Discovery & Foundation (Weeks 1–4)
- Audit OMS, carrier APIs, and CDP data readiness
- Define and contract all tool schemas
- 20 guest research interviews with Busy Parent segment
- Establish baseline metrics (WISMO volume, handle time, CSAT, cost per contact)
- Legal & privacy review — PII handling, CCPA compliance

### Phase 1 — MVP: Proactive Notifications + App Chatbot (Weeks 5–12)
**Delivers: S1, S2, S3 (v1), S7**
- S1: Proactive delay SMS/push — OMS webhook → notification pipeline
- S2: Auto-compensation engine — rule-based Circle credit on 24hr+ delay
- S3: App/web chatbot — session auth, 5 core intents, OMS + carrier tool calls
- S7: Contextual FAQ upgrade on order status page
- Rollout: 5% A/B test → measure containment rate and CSAT

> **Phase 1 Gate:** Containment rate ≥ 40% · CSAT ≥ 3.8 · Zero PII incidents

### Phase 2 — Scale: Voice IVR + Context Handoff (Weeks 13–22)
**Delivers: S4, S5, S8**
- S4: Replace legacy IVR with conversational voice agent (streaming STT → LLM → TTS)
- S5: Context handoff bundle — full transcript + case summary to Zendesk
- S8: Split shipment unified view across all packages under one order
- Full chatbot rollout to 100% of app + web traffic
- Holiday hardening: load test at 10x baseline (Black Friday ready by week 20)

> **Phase 2 Gate:** Containment rate ≥ 60% · Voice latency p95 < 2s · CSAT ≥ 4.0

### Phase 3 — Optimize: Predictive Alerting (Weeks 23–36)
**Delivers: S6 + personalization layer**
- S6: ML model trained on carrier history, weather, hub congestion, volume patterns
- Personalized tone by guest tier (Circle Plus vs. first-time guest)
- Real-time 2-hour delivery window narrowing
- Accessibility: WCAG 2.1 AA compliance, Spanish localization

### Phase 4 — Expand: Adjacent Use Cases (Month 9+)
- Return initiation within the tracking conversation
- Drive Up and Order Pickup status notifications
- Agent API open to voice assistant integrations (Google Assistant, Alexa)

---

## Success Metrics

### ⭐ North Star Metric

**WISMO Containment Rate** — the percentage of all "Where Is My Order" contacts across all channels that are fully resolved by the AI agent without human escalation.

| Timeframe | Target |
|---|---|
| 6 months | 60% |
| 12 months | 75% |

*Why this metric:* It captures self-serve effectiveness, guest trust, operational efficiency, and cost impact in a single number. Every stakeholder — product, engineering, guest care, finance — can align on it.

### Supporting Metrics

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

### 🚫 Do No Harm Guardrail Metrics

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

*Part of the [24/7 Order Status & Tracking Agent](../README.md) portfolio project · Not affiliated with Target Corporation*
