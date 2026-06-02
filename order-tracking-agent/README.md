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
- [Live Demo →](https://aistudio.google.com/apps/cf42d248-6f7d-443b-a5bc-1428bf3cbf35?fullscreenApplet=true&showPreview=true&showAssistant=true)
- [Project Structure](#-project-structure)
- [Conversation Flows](docs/conversation_flows.md)
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
