# VyaparAI — Phase 0 & Phase 1 Build Spec

Engineer-ready blueprint. No code — data models, state machines, screen states,
rules, and automation logic. This document is the source of truth for building
the "AI employee" foundation (Phase 0) and the first rules-based automations
(Phase 1).

> Product thesis: the atomic unit of VyaparAI is the **Action Card**, not the
> chat. Agents become workers that run on schedules/triggers and emit Action
> Cards into a single **Approval Inbox**. The seller reviews and approves in
> under 90 seconds each morning.

---

## A. Scope & Definition of Done

- **Phase 0 (The Spine):** the trust + action infrastructure. Nothing is "smart"
  yet — it is the rails.
- **Phase 1 (Rules-Based Automations):** three deterministic money-savers plus
  the overnight run that fills the Approval Inbox.

**Done when:** a seller opens VyaparAI in the morning, sees a ranked queue of
explained Action Cards produced overnight, approves/edits/rejects them in <90
seconds, and can undo anything — with every event captured in an audit ledger.

**North Star Metric:** autonomous actions approved per seller per week.
Secondary: hours saved per week.

---

## B. Core Data Models (entities + fields)

Field notation: `name (type) — meaning`. Enums in CAPS.

### 1. ActionCard — the atomic unit
```
id                (uuid)
created_at        (datetime)
agent             (enum: INVENTORY|PRICING|SUPPORT|RETURNS|MARKETING|LISTING|ANALYTICS)
type              (enum: REORDER|LOW_STOCK_ALERT|PRICE_FIX|PROFIT_LEAK|REPLY_DRAFT|...)
title             (string)          one-line human summary
recommendation    (string)          the concrete proposed action
subject_ref       (ref)             product_id / order_id / ticket_id it acts on
why               (Explanation)     evidence chain + numbers (see H)
impact            (Impact)          { currency_value, direction: SAVES|EARNS|PROTECTS, time_saved_min }
confidence        (int 0-100)       see H
risk_tier         (enum: GREEN|YELLOW|RED)   see F
proposed_change   (ChangeSet)       machine-executable diff (before -> after)
status            (enum: see D state machine)
autopilot_origin  (enum: SUGGESTED|AUTO_EXECUTED)
expires_at        (datetime)        stale cards auto-dismiss
group_id          (uuid, nullable)  for batch bundling ("6 price fixes")
resolution        (Resolution, nullable)  how it ended + snapshot ref
```

### 2. ChangeSet — what will actually change (enables execute + undo)
```
target            (enum: PRODUCT|PRICE|STOCK|LISTING|TICKET|PO)
target_id         (id)
before            (json snapshot of affected fields)
after             (json proposed values)
executor          (enum: INTERNAL|AMAZON|FLIPKART|EXPORT_CSV|NONE)
```

### 3. BusinessBrain — long-term memory (one per account)
```
profile:
  store_name, currency, gst_percent, gst_mode, language
  target_margin_floor_pct      hard profit guardrail
  categories[]                 with per-category margin targets
  brand_voice                  tone notes learned/edited
suppliers[]                    see model #7
preferences (learned):
  title_max_chars, price_rounding_rule, discount_floor_pct
  never_message_customers (bool), auto_approve_types[]
memory:
  decision_history[]           ref to ActivityLedger
  sku_patterns[]               winner/dog/return-prone tags
  seasonality_notes[]          Phase 3 seed; store observations now
```

### 4. ActivityLedger — immutable audit log
```
id, timestamp, actor (enum: AGENT|SELLER|SYSTEM)
agent (nullable), card_id (nullable)
action_taken (string), why (Explanation)
confidence, approved_by (nullable)
snapshot_ref (id)             for revert
outcome (enum: PENDING|SUCCESS|FAILED|REVERTED)
reverted_from (id, nullable)
```
Append-only. Never edited or deleted. This is the trust spine plus
GST/accounting proof.

### 5. Snapshot — undo payload
```
id, created_at, entity_type, entity_id
state_before (json)           full copy of mutated fields
undo_window_expires_at (datetime, nullable)  null = always reversible
```

### 6. AgentConfig — autopilot per agent
```
agent (enum)
autopilot_level (enum: MANUAL|SUGGEST|AUTO_WITH_APPROVAL|FULL_AUTO)
enabled (bool)
```

### 7. Supplier
```
id, name, contact
lead_time_days (int)
min_order_qty (int)
products_supplied[] (product_ids)
default_for_category (nullable)
```

### 8. SalesRecord (feeds velocity; even manual entry works for MVP)
```
product_id, date, units_sold, channel, sale_price, fees, gst_collected
```
MVP shortcut: if no live sales feed, derive velocity from stock deltas or let
the seller enter "sold last 7 days." Do not block Phase 1 on integrations.

### 9. GuardrailPolicy — the fence (see F)
```
margin_floor_pct
max_price_change_pct_per_run
max_reorder_value
max_actions_auto_per_night
red_tier_actions[]            always require typed confirmation
require_approval_above_impact currency threshold
```

---

## C. Extending the Existing Product model

Add to current `product`: `sku`, `cost`, `supplier_id`, `reorder_point`
(optional override), `sales_velocity_cache`, `margin_floor_override`, lifecycle
tag (`WINNER|NORMAL|DOG|RETURN_PRONE`).

---

## D. Action Card Lifecycle (state machine)

```
                 +------------+
   (agent emits) |  PROPOSED  |
                 +-----+------+
        +--------------+---------------+--------------+
        v              v               v              v
   [Approve]       [Edit]         [Snooze]        [Dismiss]
        |              |               |              |
        v              v               v              v
   +---------+   +----------+    +----------+   +----------+
   |APPROVED |   | EDITED   |    | SNOOZED  |   |DISMISSED |
   +----+----+   |(->APPROVED    |(reappears    +----------+
        |        | w/ delta)|    |  next run)|
        v        +----+-----+    +----------+
   +----------+       |
   |EXECUTING |<------+
   +----+-----+
   +----+-----------+
   v                v
+--------+     +--------+
|EXECUTED|     | FAILED |-> surfaces error card, retry/manual
+---+----+     +--------+
    v
+----------+
| REVERTED | via Undo; writes new ledger entry
+----------+
```

- **Full-Auto path:** GREEN tier + agent at `FULL_AUTO` + confidence >=
  threshold -> skips PROPOSED, goes straight to EXECUTING, lands in "Done For
  You" as EXECUTED (still undoable).
- **Auto-expiry:** PROPOSED past `expires_at` -> DISMISSED (stale).
- **Every transition writes an ActivityLedger row.**

---

## E. Approval Inbox — Screen States

Layout: three stacked zones (this home screen replaces the chat as the default).

- **Zone 1 — Needs You** (sorted by currency impact desc): cards in
  PROPOSED / SNOOZED-returned. Batch header: `Approve all high-confidence (n)`.
- **Zone 2 — Done For You:** EXECUTED auto-actions from the last run. Each shows
  Undo. Collapsible.
- **Zone 3 — Watching:** sub-threshold trends ("3 SKUs approaching low stock in
  ~10 days"). No action yet.

### Screen states to design
| State | Condition | UI |
|---|---|---|
| Loading | overnight run in progress | skeleton + "Reviewing your store..." |
| All-clear | no pending cards | "You're all caught up. I completed N tasks overnight." (hero, not empty-sad) |
| Populated | >=1 pending | ranked cards, batch bar |
| First-run / no data | new account | onboarding: connect data, set margin floor, set autopilot levels |
| Error | run failed | "I couldn't finish the overnight review - [retry]. Nothing was changed." |
| Post-approve | seller cleared queue | animate to All-clear + "Saved you ~X hrs / currency Y today" |

### Card interactions (keyboard-first)
`A` approve · `E` edit (opens pre-filled) · `X` dismiss · `S` snooze · `?`
expand Why. Target: clear queue in <90s.

---

## F. Guardrail / Policy Engine (risk tiers)

Every card is assigned a tier at creation. Tier + autopilot level + confidence
decides routing.

| Tier | Examples | Routing rule |
|---|---|---|
| GREEN (reversible, low-stakes) | SEO tag update, reply *draft*, price change within +/-X% and above margin floor | Eligible for FULL_AUTO if confidence >= threshold |
| YELLOW (meaningful, reversible) | Reorder PO, publish listing, price change beyond +/-X%, marketing spend | Always requires approval |
| RED (irreversible / external-facing) | Issue refund, send message to a customer, bulk delist, price change breaching floor | Typed confirmation, never auto - ever |

**Hard limits the engine enforces before a card can execute:**
- Reject/downgrade any price change that would breach `margin_floor_pct`.
- Cap auto actions at `max_actions_auto_per_night`.
- Block reorder if value > `max_reorder_value` -> force YELLOW.
- Any action touching a customer -> RED regardless of confidence.

Guardrails are seller-editable but have safe defaults. The AI operates strictly
inside this fence.

---

## G. Phase 1 Automations (trigger -> logic -> card)

Each spec = Trigger, Inputs, Logic (plain language), Output card, Confidence,
Tier.

### G1. Low-Stock Detection + Days-of-Cover
- **Trigger:** overnight run; also on stock-change event.
- **Inputs:** current stock, sales velocity (units/day, trailing 30d), supplier
  lead_time.
- **Logic:** `days_of_cover = stock / velocity`. If
  `days_of_cover <= lead_time + safety_buffer` -> flag.
- **Card:** LOW_STOCK_ALERT -> "Kurta-Blue: 6 days of cover left." Impact =
  PROTECTS (value = velocity x price x expected stockout days).
- **Confidence:** high if >=30 days of stable sales data; lower if sparse or
  volatile.
- **Tier:** GREEN (alert only). Pairs with G2.

### G2. Reorder Recommendation
- **Trigger:** fires with a G1 flag.
- **Inputs:** velocity, lead_time, min_order_qty, target cover days, supplier.
- **Logic:** `reorder_qty = ceil(velocity x (lead_time + target_cover)) -
  stock_on_hand`, rounded to `min_order_qty`. Timing: order by
  `today + (days_of_cover - lead_time)`.
- **Card:** REORDER -> "Order 120 units from Supplier A by Thursday." Includes a
  draft PO in `proposed_change` (executor = EXPORT_CSV / email for MVP).
- **Confidence:** function of velocity stability + data volume.
- **Tier:** YELLOW (always approval); RED if value > `max_reorder_value`.

### G3. Profit-Leak Detection
- **Trigger:** overnight run.
- **Inputs:** cost, sale price per channel, channel fee %, gst (mode), returns
  rate.
- **Logic:** `real_margin = sale_price - cost - (sale_price x fee%) -
  gst_component - (returns_rate x cost)`. If `real_margin_pct < margin_floor`
  -> leak.
- **Card:** PROFIT_LEAK -> "You're netting only 4% on Myntra for Kurta-Blue
  (floor 15%). Raise to X or pause channel." `proposed_change` = price bump to
  hit floor.
- **Confidence:** high (deterministic math on known numbers).
- **Tier:** GREEN if fix stays within +/-X% and above floor; else YELLOW.

### G4. Overnight Run + Morning Digest
- **Trigger:** scheduler (seller's timezone, e.g. 5 AM) + manual "Run now."
- **Orchestration order:** refresh velocities -> G1 -> G2 -> G3 -> (future
  agents) -> Max prioritizes: rank by currency impact, bundle by type into
  `group_id`, assign tiers, auto-execute eligible GREEN, queue the rest.
- **Dedup:** if an identical PROPOSED card exists from a prior run, update it
  (do not duplicate).
- **Digest output:** "Completed N, Needs approval M, Impact X, ~Y hrs saved."
  Delivered as in-app banner + optional email/WhatsApp.

---

## H. Confidence & Explanation Standards (apply to ALL cards)

**Confidence (0-100)** = blend of:
1. Data sufficiency (how much history backs it),
2. Signal stability (variance / volatility),
3. Historical accuracy of this card type for this seller (Phase 2 feeds this
   back).

Must be calibrated - track predicted vs actual accuracy; display honestly.

**Explanation object (mandatory on every card):**
```
summary        (one plain-language sentence)
evidence[]     (the data points cited, with numbers)
assumptions[]  (e.g. "assumes lead time 5 days")
what_if_wrong  (worst case if seller approves and it is wrong)
```
No card may exist without a populated `why`. This is what earns Full-Auto trust.

---

## I. Undo Mechanics

- Before any EXECUTING transition, persist a Snapshot of affected fields.
- Revert restores `state_before`, sets card -> REVERTED, writes a new ledger row
  (never erases history).
- External executors (Amazon/Flipkart) in Phase 1 are still dry-run/export, so
  undo is trivial; when live (Phase 4), revert issues the compensating API call.
- Undo window: GREEN = always; YELLOW = 24h default; RED = N/A (required
  confirmation up front).

---

## J. Acceptance Criteria (Definition of Done)

### Phase 0
- [ ] Action Card renders with all 6 anatomy elements (what/why/impact/confidence/tier/actions).
- [ ] Approve/Edit/Dismiss/Snooze transitions work + write ledger.
- [ ] Undo restores prior state and logs a revert.
- [ ] Autopilot levels + guardrail limits enforced (a floor-breaching price change is blocked in tests).
- [ ] Approval Inbox renders all 6 screen states.
- [ ] Business Brain persists profile + preferences across sessions.

### Phase 1
- [ ] Overnight run produces cards for G1-G3 on seed data.
- [ ] Reorder qty/timing math verified against hand-calculated cases.
- [ ] Profit-leak flags a known below-floor SKU and proposes a floor-hitting price.
- [ ] Morning Digest shows accurate counts + currency impact + hrs saved.
- [ ] GREEN full-auto executes only within guardrails; YELLOW/RED never auto-execute.

---

## K. Open Decisions (need a call before build)

1. **Sales data source for velocity** - live marketplace pull (Phase 4), CSV
   import, or manual "units sold last 7 days" for MVP? (Recommend: manual/CSV
   now - do not block on APIs.)
2. **Digest channel** - in-app only, or add email/WhatsApp from day one?
   (WhatsApp is huge for Indian sellers - strong V1 differentiator.)
3. **Default autopilot** - ship everything at SUGGEST (safe) and let sellers
   graduate? (Recommend yes.)
4. **Undo window lengths** - confirm defaults above.
5. **PO execution in MVP** - email to supplier vs CSV/PDF PO the seller sends?

---

## Appendix: Feature Elimination (context for scope)

- Demote chat to a command bar; the Approval Inbox is the home screen.
- Merge SEO into Listing (SEO is a listing-quality attribute, not a job).
- Replace analytics-as-graphs with the action feed; charts live only inside a
  card as evidence.
- On-demand caption generation becomes trigger-based (new product, festival,
  dead ad), not free-form.
- "List Everywhere" evolves from a text dump into real queued + approved +
  executed/exported actions.
- Hide the 9-agent org chart from daily UI; expose actions, not employees.
