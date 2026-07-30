# VyaparAI — Product Principles

The single rule that governs what we build.

---

## The Feature Gate

> **Never build a feature simply because it sounds impressive.**

Before ANY feature is designed, built, or merged, it must answer all four
questions. If it cannot, it is **not implemented** — no exceptions, no "but the
demo looks cool."

1. **Which employee does it replace?**
   (inventory planner, pricing analyst, support agent, marketer, finance/ops...)
2. **How many hours does it save per week?**
   (a concrete number, per seller)
3. **Why would a business owner pay monthly for it?**
   (the recurring pain it removes, in money or time)
4. **Is it MVP, V2, or Future?**

If the honest answer to 1–3 is "none / unclear / because AI," **kill the
feature.**

---

## Why this rule exists

VyaparAI wins by being an **AI employee that replaces repetitive back-office
work**, not an AI chatbot that generates content on request. Value is measured
in **labor replaced and money/time saved**, never in novelty. Every impressive-
sounding-but-useless feature we skip keeps the product focused and keeps the
seller's daily 90-second approval ritual fast.

---

## The Gate applied (worked examples)

### PASS — build these
| Feature | Replaces | Hours/wk saved | Why pay monthly |
|---|---|---|---|
| Stockout prediction + reorder | Inventory planner | 3–5 | Protects revenue from stockouts + dead capital |
| Profit-leak detection | Finance analyst | 2–4 | Finds real money lost to fees/GST every week |
| Approval Inbox + overnight run | Ops assistant | 5–10 | The core "runs my store for me" value |
| Dissatisfaction / SLA detection | Support agent | 3–6 | Protects marketplace rating (existential) |
| High-return root-cause | QA / ops | 1–3 | Recovers margin, fixes bad listings |

### FAIL / DEMOTE — do not build (or strip back)
| Feature | Why it fails the gate |
|---|---|
| Free-form "chat with the AI" as the main UI | Replaces no employee; reactive; saves no guaranteed hours |
| On-demand random caption generator | No recurring pain; a one-off toy, not a job replaced |
| Graph/analytics dashboards | Nobody acts on a chart; replaces no labor. Convert to Action Cards or delete |
| "Talk to 9 named agent personalities" | Charm, not value; adds cognitive load without saving time |
| Any feature justified by "it's AI-powered" | Novelty is not a reason to pay monthly |

---

## How to use this doc

- In every spec/PR, include the **Feature Gate answers** for each new capability.
- Reviewers reject anything that ships without passing the gate.
- When in doubt, ask: *"Would a real Shopify/Amazon seller pay for this every
  month because it does a job they'd otherwise hire someone for?"* If not, cut
  it.
