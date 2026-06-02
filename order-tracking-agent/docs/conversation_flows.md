# Conversation Flows — 24/7 Order Status & Tracking Agent
# Version 1.0 · Phase 1 MVP

This document details all 5 conversation flows the agent handles in v1, including decision trees, tool call sequences, and response guidelines for each state.

---

## Flow 1 — WISMO (Where Is My Order?)

**Triggers:** "Where's my order?", "When is my order coming?", "Has my order shipped?", "Track my package", "What's the status of my order?"

```
Guest asks about order
        │
        ├─ Has order_id? ──YES──► call get_order_status(order_id)
        │
        └─ No order_id ──────────► call get_customer_orders(customer_id)
                                          │
                                   1 recent order? ──YES──► call get_order_status for it
                                          │
                                     Multiple orders? ──────► ask guest to confirm which one
                                                                    │
                                                             get_order_status for confirmed order
```

**Status → Response mapping:**

| OMS Status | What agent says |
|---|---|
| `label_created` | "Your order has been packed and a shipping label has been created. It should be picked up by [carrier] soon." |
| `in_transit` | "Your order is on its way with [carrier]. Latest scan: [location], [timestamp]." |
| `out_for_delivery` | "Great news — your order is out for delivery today and should arrive by [ETA]." |
| `delivered` | "Your order was delivered on [date] at [time]. Did you receive it okay?" |
| `delayed` | → Trigger **Flow 2: Delay Protocol** |
| `cancelled` | "This order was cancelled on [date]. [Offer to check if item is still available]." |
| `label_created` for Drive Up | → Check if fulfillment_type=drive_up and route to **Flow 5** |
| `order_ready` | → Route to **Flow 5: Drive Up / Pickup** |

**Tool call sequence for shipped order:**
1. `get_customer_orders` (if no order_id given)
2. `get_order_status`
3. `get_tracking_info` (only if status is in_transit, out_for_delivery, or delivered)

**Always end with:** "Is there anything else I can help you with?"

---

## Flow 2 — Delay Protocol

**Triggers:** Order status = `delayed`, OR guest says order is late and OMS confirms

```
Delay detected
      │
      ├─ Get delay details: new ETA, reason, prior_delay_count
      │
      ├─ prior_delay_count >= 1? ──YES──► Offer compensation credit (log for processing)
      │
      ├─ hours_past_original_eta >= 48? ──YES──► escalate_to_human (auto, even without request)
      │
      └─ Otherwise:
             │
             ├─ Acknowledge with specific empathy (name the item + original ETA)
             ├─ State new ETA and reason
             ├─ Offer notification opt-in
             └─ End with offer to help further
```

**Delay reason → Plain English:**

| Delay Reason Code | What agent says |
|---|---|
| `weather_disruption` | "There's a weather delay affecting [carrier] in your area." |
| `carrier_volume_surge` | "High shipping volume is causing delays across [carrier]'s network right now." |
| `hub_issue` | "There's a delay at one of [carrier]'s sorting facilities." |
| `address_issue` | "There may be a question about your delivery address — I'd like to get this cleared up." |
| `customs_hold` | "Your package is currently being processed through customs — this typically resolves within 1–2 business days." |
| `null` / unknown | "I can see there's a delay but don't have a specific reason yet. Here's the latest we know:" |

**Tone rules for delay responses:**
- ❌ Never: "I apologize for the inconvenience"
- ❌ Never: "due to unforeseen circumstances"
- ✅ Always: Name the specific item — "your Dyson vacuum", not "your order"
- ✅ Always: Reference the original ETA — "was supposed to arrive yesterday"
- ✅ Always: Give a concrete next step — offer notification or escalation

---

## Flow 3 — Split Shipment Confusion

**Triggers:** "Where's the rest of my order?", "I only got part of my delivery", "Why did my order come in separate packages?"

```
get_order_status
      │
      split_shipments: true?
      │
      YES ──► Present each shipment group separately:
                    │
                    For each group:
                    ├─ status=delivered → "✓ [Items] — delivered [date]"
                    └─ status=in_transit → call get_tracking_info(shipment_group_id)
                                                │
                                           Present tracking for that group
      │
      NO ──► Treat as single shipment (route to Flow 1 or Flow 4 based on status)
```

**Presentation format for split shipments:**

```
Your order has 2 packages — here's where each one is:

Package 1 — Samsung 65" TV
✓ Delivered Jun 2 at 2:30 PM via FedEx

Package 2 — TV Wall Mount + HDMI Cable
◉ In transit via UPS · Arriving Jun 4
   Current location: Columbus, OH
```

**Edge cases:**
- One package delivered, another in normal transit → Inform only, do NOT escalate
- One package delivered, another shows no movement for 5+ days → Escalate with reason "delayed_partial_shipment"
- Guest says they received a wrong item in one package → Out of scope for v1, route to returns

---

## Flow 4 — "Marked Delivered But Not Received"

**Triggers:** "My order says delivered but I didn't get it", "Shows as delivered but nothing arrived", "Package is missing"

```
get_order_status → status=delivered
      │
      get_tracking_info
      │
      ├─ hours_since_delivery < 24?
      │       └─ Give 3-step check list. Advise to wait 24hrs before filing claim.
      │          Set expectation: "Let me know if you still can't find it tomorrow."
      │
      └─ hours_since_delivery >= 24?
              └─ Give 3-step check list
                 escalate_to_human(reason="package_not_received", sentiment="high")
                 Do NOT promise refund or reship
                 Do NOT close session
```

**3-step check list (always give this first):**
1. Check all delivery locations at your address — front door, back door, garage, mailroom, leasing office
2. Check with neighbors — sometimes packages are left at nearby units by mistake
3. Look for a "delivery attempted" notice card — the carrier may have left it somewhere visible

**What NOT to do:**
- Do not promise a refund in v1 — this requires human agent authorization
- Do not promise a reship in v1 — same reason
- Do not imply the carrier is at fault — keep it neutral
- Do not suggest the guest is lying — keep tone collaborative and believing

---

## Flow 5 — Drive Up & Order Pickup

**Triggers:** "Is my Drive Up order ready?", "Can I pick up my order?", "Ready for pickup?", "How long until my order is ready?"

```
get_order_status → fulfillment_type in [drive_up, order_pickup]
      │
      ├─ status = "processing"
      │       └─ "We're preparing your order — it should be ready within [prep_time] minutes."
      │
      ├─ status = "being_picked"
      │       └─ "A team member is picking your order right now — it'll be ready very soon!"
      │
      ├─ status = "order_ready"
      │       └─ "Your order is ready! [Store name]. Your pickup code: [code]."
      │          Remind hold period: Drive Up = 2 days, Order Pickup = 3 days
      │
      └─ status = "hold_expired"
              └─ "Your pickup window has passed and the order was cancelled.
                 I can help you reorder if you'd like — would that be helpful?"
```

**Drive Up vs Order Pickup differences to communicate:**

| Aspect | Drive Up | Order Pickup |
|---|---|---|
| Where | Park in Drive Up spot | Come inside to Guest Service Desk |
| Hold period | 2 days | 3 days |
| What to bring | Your phone (app) | Pickup code or ID |
| Tip | Park in the Drive Up designated spots near the entrance | Look for the Guest Service Desk sign inside |

**Do NOT call get_tracking_info** for Drive Up or Order Pickup orders — there is no carrier involved. Calling it will return an error.

---

## Escalation Decision Tree

```
Any conversation turn
      │
      ├─ "I want a human" / "speak to a person" ──────────────────────────► ESCALATE (guest_requested)
      │
      ├─ Anger + prior_delay_count >= 1 ──────────────────────────────────► ESCALATE (high_frustration_repeat_delay)
      │
      ├─ hours_past_original_eta >= 48 ───────────────────────────────────► ESCALATE (auto_48hr_delay)
      │
      ├─ status=delivered + hours_since_delivery >= 24 + "didn't receive" ─► ESCALATE (package_not_received)
      │
      ├─ Resolved same issue twice in session, still unresolved ──────────► ESCALATE (unresolved_after_two_attempts)
      │
      ├─ Guest says "urgent", "medical", "emergency", "lawyer", "BBB" ─────► ESCALATE (guest_requested, sentiment=high)
      │
      └─ None of the above ───────────────────────────────────────────────► Continue conversation
```

**Escalation response template:**

```
[Acknowledge the situation with empathy]

I'm connecting you with a senior team member right now — they'll be able to make this right.

Your case ID is [CASE_ID]. They'll have everything from our conversation, so you won't need to repeat yourself. 

Estimated wait: [X] minutes.
```

---

## Out-of-Scope Response Templates (v1)

**Returns request:**
"For returns, the fastest path is through the app under Orders → Start a Return, or I can connect you with our returns team. Which would you prefer?"

**Payment / billing question:**
"Payment questions are handled by a specialist team — I can connect you with them right away. Would that help?"

**Product availability / recommendations:**
"I'm focused on order tracking, but product details and availability are easy to find in the app's search or at [website]. Anything else order-related I can help with?"

**Address change after shipment:**
"Once an order ships, address changes go directly through the carrier. For FedEx, you can redirect at fedex.com/en-us/delivery-options.html. For UPS, it's ups.com/redirectpackage. Want me to look up which carrier your order is with?"

**Cancellation request (after shipment):**
"Unfortunately, orders that have already shipped can't be cancelled. Once it arrives, you can return it through the app for a full refund. I can walk you through that when it gets there."

**Cancellation request (before shipment):**
"This one hasn't shipped yet — I can flag your cancellation request. [Note: in v1, log this for human review; do not attempt to cancel via API.] You'll receive a confirmation email within 1 hour."