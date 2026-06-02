# Impact × Effort Matrix — 24/7 Order Status & Tracking Agent

> **⚠️ Disclaimer:** This is a **personal AI learning project** created for portfolio purposes. This is **not** Target Corporation's official product, use case, or repository. I have no affiliation with Target's engineering or product teams. All Target branding references are used solely for illustrative purposes in a product design exercise. Mock data, personas, and scenarios are entirely fictional.

---

## The Framework

Every solution was evaluated on two axes before being assigned to a phase:

- **Impact** — How much does this move the North Star metric (WISMO Containment Rate) and directly relieve the chosen pain point (Pain Point #1: No proactive delay communication)?
- **Effort** — How much engineering, design, and cross-functional coordination does this require to ship in production?

The goal is to sequence solutions so that high-impact, low-effort work ships first (Phase 1), creates measurable results, and funds the investment needed for high-effort strategic bets (Phase 2–3).

---

## The Matrix

```
HIGH IMPACT
    │
    │         QUICK WINS                    STRATEGIC BETS
    │         ───────────────────           ──────────────────────
    │         S1 Proactive SMS/push         S3 App/web AI chatbot
    │         S2 Auto-compensation          S4 Voice IVR deflection
    │         S7 Contextual FAQ upgrade     S5 Seamless agent handoff
    │                                       S6 Predictive delay ML
    │
    │         FILL-INS                      DEPRIORITIZE
    │         ──────────────────            ──────────────────────
    │         S8 Split shipment view        S9  WhatsApp channel
    │                                       S10 Email response bot
LOW IMPACT
             LOW EFFORT ─────────────────────────────── HIGH EFFORT
```

---

## All Solutions — Full Detail

### S1 — Proactive Delay SMS / Push Notification
**Quadrant:** Quick Win · **Phase:** 1 · **Effort:** Low · **Impact:** Very High

**What it is:** When the OMS or a carrier webhook detects a delay event, automatically trigger a personalised SMS or push notification to the guest with the new ETA, a plain-English reason, and a deep-link back to the agent for self-serve follow-up.

**Why it directly addresses Pain Point #1:** The "surprise wait" happens because the guest has no idea their order is delayed until after the delivery window closes. This solution eliminates that entirely — the guest is informed before frustration sets in, before they call in, before the emotional temperature rises. It converts a reactive, high-cost contact into a proactive, zero-cost notification.

**Why it's Low Effort:** The OMS already emits status change events. Carrier webhooks are standard integrations. The notification pipeline (Twilio for SMS, Firebase for push) is commodity infrastructure. No AI or ML required — this is a webhook listener + template renderer + notification sender. An experienced backend engineer can ship this in 2–3 weeks.

**Why it's Very High Impact:** It directly attacks the root cause of the highest-frequency, highest-emotion pain point. Every notification sent is a WISMO call that doesn't happen. At scale, this single solution can reduce inbound contact volume by 15–25% on its own, before the chatbot is even built.

**Risks:** Notification fatigue if over-triggered. Guest opt-out rates must be monitored. Must not fire on false delay signals from carrier data lag.

---

### S2 — Auto-Compensation on Verified 24hr+ Delay
**Quadrant:** Quick Win · **Phase:** 1 · **Effort:** Low–Medium · **Impact:** High

**What it is:** If a delay exceeds 24 hours past the original ETA, automatically trigger a store credit or loyalty discount code and include it in the delay notification — before the guest complains.

**Why High Impact:** Proactive compensation before the guest asks for it is one of the highest-trust gestures a brand can make. It signals accountability. Research consistently shows that proactive recovery — reaching out first — has a stronger positive CSAT impact than reactive recovery where the guest had to demand something. It also reduces the escalation rate by removing the financial grievance that would otherwise require a human to resolve.

**Why Low–Medium Effort:** Requires a compensation rules engine (rule: delay > 24hrs AND prior_delay_count = 0 → issue $5 credit) and integration with the loyalty / promotions platform. More complex than S1 because it touches the financial system, but still well within a sprint-sized scope. Guardrails needed to prevent abuse (max one auto-credit per order, not triggered on delays caused by incorrect guest address).

**Risks:** Compensation over-triggering (false delay signals, address-related delays where liability is guest's). Requires P&L sign-off on the per-incident cost vs. the retention and escalation-avoidance value.

---

### S3 — App / Web Conversational AI Chatbot (Core Agent)
**Quadrant:** Strategic Bet · **Phase:** 1–2 · **Effort:** High · **Impact:** Very High

**What it is:** The primary AI agent surfaced in the retailer's app and on the website. Handles WISMO queries conversationally using session-based authentication, calling `get_order_status`, `get_tracking_info`, and `get_customer_orders` tools. Resolves the full interaction end-to-end without a human for 75%+ of contacts.

**Why Very High Impact:** This is the core product. It is the mechanism by which 60–75% of WISMO contacts are contained without human involvement. Every other solution either feeds into it (S1 generates deep-links that land in the chatbot), supports it (S5 improves escalation handoffs), or extends it (S6 gives it predictive data). It is the North Star metric engine.

**Why High Effort:** Requires: LLM selection and prompt engineering, tool schema design and backend integration (OMS, carrier APIs, CDP), session state infrastructure (Redis), frontend widget integration across app and web, QA test suite, A/B rollout infrastructure, PII compliance review, and load testing. This is a multi-team, multi-sprint initiative. However, with a platform like Google AI Studio and a well-written system prompt, a working prototype can be built in days — the effort is in hardening it for production scale.

**Phased approach:** Ship the app/web chatbot in Phase 1 with text-only input. Add voice (S4) in Phase 2. This lets the team validate containment rate and CSAT on the core flows before investing in the more complex voice infrastructure.

**Risks:** Agent accuracy on edge cases (split shipments, multi-order households). Prompt injection attempts. Carrier API latency degrading response time. PII handling in conversation logs.

---

### S4 — Voice IVR AI Deflection
**Quadrant:** Strategic Bet · **Phase:** 2 · **Effort:** Very High · **Impact:** Very High

**What it is:** Replace the legacy IVR phone tree on the inbound customer service line with a conversational voice AI agent. Guests speak naturally — "I want to check on my order from last Tuesday" — and the agent resolves without hold time or menu navigation.

**Why Very High Impact:** Phone is the highest-volume WISMO channel and the highest-cost one. Human-handled phone calls cost significantly more per contact than chat interactions. Voice also carries the highest emotional intensity — a guest who has been on hold for 12 minutes arrives at a human agent already frustrated. Eliminating hold time entirely for WISMO calls transforms the guest experience at the highest-leverage point.

**Why Very High Effort:** Requires: bidirectional audio streaming infrastructure (Gemini Flash Live or equivalent), STT/TTS pipeline optimisation for retail vocabulary (order IDs, carrier names, product names), barge-in handling (guest talking over the agent), low-bandwidth audio fallback, telephony integration (Twilio, Genesys, or Five9), and rigorous accessibility testing. The voice experience is significantly harder to get right than text chat — misheard words, ambiguous pronunciation of order numbers, and background noise all create failure modes that don't exist in text.

**Why Phase 2, not Phase 1:** The chatbot (S3) must be proven first. Voice has the same tool integrations and agent logic — it is the same agent with a different input/output modality. Validate the logic in text, then extend to voice. This avoids spending very high effort on voice if the core agent logic has fundamental issues.

**Risks:** Latency. Every additional 100ms of audio latency is perceptible to the guest. The p95 target of < 1.5 seconds is aggressive. STT accuracy on names, addresses, and order IDs. Guest frustration if the voice agent misunderstands and loops.

---

### S5 — Seamless Agent Context Handoff to Human
**Quadrant:** Strategic Bet · **Phase:** 2 · **Effort:** Medium · **Impact:** High

**What it is:** When the AI escalates to a human agent, automatically push a structured context bundle to the helpdesk (Zendesk/Salesforce) containing: full conversation transcript, all order IDs discussed, guest sentiment level, compensation already offered, and a one-line case summary written by the AI. The human agent picks up the case already fully briefed.

**Why High Impact:** The single most common complaint about AI escalations is "I had to repeat everything to the human agent." This failure mode destroys whatever trust the AI interaction built — the guest ends the call more frustrated than if they had spoken to a human from the start. Eliminating it entirely is a step-change improvement in CSAT for escalated cases, which are already the highest-risk interactions.

**Why Medium Effort:** Requires Zendesk/Salesforce API integration for case creation, a context bundle schema, and the escalation tool's output formatting. The AI already has all the context — the engineering work is in the integration and the handoff UI that the human agent sees. Achievable in one sprint with a focused integration engineer.

**Risks:** Helpdesk API rate limits under peak escalation volume. Context bundle must be concise — human agents don't read 3,000-word transcripts. The one-line summary quality depends on the AI's ability to distil the key issue accurately.

---

### S6 — Predictive Delay Alerting (ML Model)
**Quadrant:** Strategic Bet · **Phase:** 3 · **Effort:** Very High · **Impact:** Very High

**What it is:** Train an ML model on historical carrier performance data, weather API signals, hub congestion metrics, and order volume patterns to predict likely delays 12–24 hours before they are officially confirmed by the carrier. Alert guests pre-emptively.

**Why Very High Impact:** This takes the proactive model from S1 (reactive to confirmed delay events) to genuinely anticipatory. A guest who learns their order might be a day late — before they've arranged their schedule around the delivery — has a fundamentally different emotional experience than one who learns after waiting all day. It is the highest trust signal the product can send: "We knew before you did, and we told you."

**Why Very High Effort:** Requires: historical data pipeline (years of carrier + order + weather data), feature engineering, model training and validation, real-time inference infrastructure, and a feedback loop to improve model accuracy over time. This is a dedicated ML engineering project, not a sprint task. The model also has high-stakes accuracy requirements — false positives (predicting delays that don't happen) create unnecessary anxiety; false negatives (missing delays) reduce trust in the alerts.

**Why Phase 3:** S1 must be live and generating notification data for months before S6 can be trained with sufficient signal. The model also requires the logging infrastructure from Layer 7 to be mature. Phase 3 sequencing is correct.

**Risks:** Model drift as carrier performance patterns change seasonally. Weather data API reliability. Guest fatigue from over-alerting if precision is low. Requires sustained ML engineering investment.

---

### S7 — Contextual Tracking FAQ Upgrade
**Quadrant:** Fill-in · **Phase:** 1 · **Effort:** Low · **Impact:** Medium

**What it is:** Upgrade the static order status page with dynamic, state-aware FAQ cards. If the order is delayed, show "What do I do now?" options. If marked delivered, show the missing package flow. If out for delivery, show "Can I change my delivery instructions?"

**Why Medium Impact:** It doesn't require the full AI agent but it deflects a meaningful slice of follow-up contacts that happen immediately after a guest checks their order status. A guest who sees "delayed" and immediately has a "here's what happens next" guide is less likely to call in than one who sees "delayed" and has no context.

**Why Low Effort:** This is frontend content changes — no AI, no backend, no new integrations. A frontend engineer and a content designer can ship this in a single sprint alongside Phase 1 development. It is the fastest way to reduce WISMO-adjacent contact volume before the chatbot is live.

---

### S8 — Split Shipment Unified Tracking View
**Quadrant:** Fill-in · **Phase:** 2 · **Effort:** Medium · **Impact:** Medium

**What it is:** A single consolidated view showing all packages under one order — each item's location, ETA, and carrier — instead of requiring guests to track multiple numbers separately.

**Why Medium Impact:** Split shipment confusion (Pain Point #4) is a high-frequency issue but not the primary driver of escalations. Solving it cleanly in the chatbot (Flow 3 in the system prompt) addresses the AI agent path. This solution addresses the self-serve path on the order status page for guests who don't use the chatbot.

**Why Medium Effort:** Requires OMS integration changes to surface split shipment data in a single API response, and frontend work to render the unified view. More effort than S7 because it involves backend changes, but simpler than S3–S5 because it is a read-only display problem with no conversational complexity.

---

### S9 — WhatsApp Conversational Channel
**Quadrant:** Deprioritized · **Phase:** TBD · **Effort:** High · **Impact:** Low–Med (US market)

**What it is:** A WhatsApp Business API integration that allows guests to check order status via WhatsApp chat.

**Why Deprioritized:** WhatsApp has very high penetration internationally but the domestic US retail guest base is predominantly app and SMS native. The engineering complexity — Meta Business API compliance, approved message template approval process, session window restrictions (24-hour window), and data residency requirements — is high relative to the incremental reach. The app chatbot (S3) and SMS (S1) serve the same communication need for the US audience at lower cost and complexity.

**Revisit trigger:** International expansion or evidence that a significant guest segment prefers WhatsApp over the app or SMS.

---

### S10 — Email Response Bot
**Quadrant:** Deprioritized · **Phase:** TBD · **Effort:** High · **Impact:** Low

**What it is:** An AI agent that parses inbound order-related emails and sends automated responses with order status information.

**Why Deprioritized:** Email is a fundamentally asynchronous channel — guests who care enough to check their order status don't wait 24 hours for an email reply. By the time the email bot responds, the guest has either already called in (and the call is the more emotionally impactful interaction to resolve) or self-served via the app. The engineering complexity of stateful email conversations — threading, reply parsing, session management without persistent auth — is high, and the deflection ROI vs. app/voice channels is minimal for real-time order status queries.

---

## Sequencing Rationale

The phasing above was chosen to satisfy three constraints simultaneously:

**Constraint 1 — Speed to impact.** Phase 1 must show measurable reduction in WISMO contact volume within 12 weeks. S1 and S2 can ship within the first 4–6 weeks and begin deflecting contacts before the chatbot (S3) is fully live. This creates early evidence to sustain stakeholder confidence and budget.

**Constraint 2 — Risk sequencing.** Higher-effort, higher-risk solutions (S4 voice, S6 ML) come after the simpler solutions have validated the core data integrations (OMS, carrier APIs, CDP). If the carrier API has data quality issues, it is far better to discover this during S3 text-chat testing than during S4 voice rollout.

**Constraint 3 — Learning dependency.** S6 (predictive ML) cannot be trained without the event data that S1 and S3 generate. S4 (voice) should not be built until S3 proves the agent logic is sound. The phase sequence respects these dependencies.

---

*Part of the [24/7 Order Status & Tracking Agent](../README.md) portfolio project · Not affiliated with Target Corporation*
