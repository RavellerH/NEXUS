---
id: open-questions
type: tracker
status: active
last_updated: 2026-05-29
related:
  - ./decisions.md
  - ./todo.md
  - ./INDEX.md
---

# Open Questions

> Questions that are unanswered and block specific design or implementation decisions.
> When a question is answered, move it to [decisions.md](./decisions.md) and mark it `resolved` here.

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| 🔴 | Blocking — cannot proceed without answer |
| 🟡 | Important — affects design but has a safe default |
| 🟢 | Nice to know — low urgency |

---



## Q4 — Setup Service

**Status**: 🟡 Important
**Priority**: Medium
**Blocks**: Onboarding flow design, pricing add-on structure

### Question
Does the purchase include a done-for-you VPS setup, or is it fully self-serve?

### Why it matters
The gap between "self-hosted" and "non-technical PM" is real. Even with a perfect Docker Compose bundle, setting up a DigitalOcean droplet, configuring DNS, and running first-time setup requires comfort with a terminal. A PM buying this product may not have that comfort.

### Options
- **Fully self-serve** — works if setup guide is extremely good and one-command setup actually works
- **Paid setup add-on** — e.g., Rp 500K–1 juta for first deployment; removes the biggest adoption barrier; common in SEA software market
- **Free setup for first N clients** — good for getting testimonials and learning what breaks

### Recommended
Offer paid setup as an optional add-on. Keep the self-serve path working in parallel. Early clients: do the setup for free to learn failure modes.

### Related
- [business/model.md](./business/model.md)
- [business/infrastructure.md](./business/infrastructure.md)
- [todo.md → Phase 1](./todo.md)

---

## Q5 — Buyer: Personal or Company Procurement

**Status**: 🟡 Important
**Priority**: Medium
**Blocks**: Payment flow design, invoicing, sales process

### Question
Is the actual buyer the PM personally (personal bank transfer / credit card), or their company (invoice to accounts department + procurement process)?

### Why it matters
In SEA EPC firms, software purchases above a threshold go through procurement. This means:
- Payment by bank transfer (invoice), not credit card
- Signed agreement or PO may be required
- Decision maker (PM) is not the same person as budget approver (finance)
- Sales cycle is longer but deal size can be higher

### Options
- **Individual buyer** → Gumroad/LemonSqueezy/Stripe; fast; low friction; limits deal size
- **Company buyer** → Invoice-based; slower; higher deal size; requires proper invoicing and contract templates

### Recommended
Design for **company buyer** (invoice + transfer). Most EPC PMs in Indonesia will not use a personal card for business software. Build a simple invoice template and WhatsApp-friendly sales flow.

### Related
- [business/model.md](./business/model.md)
- [business/market.md](./business/market.md)

---

## Resolved Questions

*Answered questions are moved here for reference. Full rationale in [decisions.md](./decisions.md).*

| Question | Answer | Date |
|----------|--------|------|
| SaaS or self-hosted? | Self-hosted | 2026-05-29 |
| Team size per PM? | 5–10 field engineers | 2026-05-29 |
| Projects per PM? | Many concurrent | 2026-05-29 |
| Primary market? | SEA — Indonesia, Malaysia, Philippines | 2026-05-29 |
| Deployment target? | Client's own VPS | 2026-05-29 |
| WhatsApp staleness tolerance? | Daily is fine; 2+ days = team issue | 2026-05-29 |
| Distribution model? | Digital product (deployable package) | 2026-05-29 |
| WhatsApp Chat Language | Multilingual (code-switching between Bahasa & English) | 2026-05-29 |
| Distribution Format | Shipping a zip file / Private GitHub repo | 2026-05-29 |
| License Pricing Model | Recurring annual/monthly renewal | 2026-05-29 |
