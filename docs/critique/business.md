---
id: critique-business
type: narrative
status: active
last_updated: 2026-05-29
related:
  - ../business/model.md
  - ../business/market.md
  - ./technical.md
  - ../open-questions.md
---

# Business Critique

> Pain points identified during product review. Each item has an associated recommendation or decision.

---

## B01 — "One docker-compose up" Promise Is Not Real Yet

**Severity**: High
**Status**: Open — must be fixed in Phase 1

The README promises one-command startup. Reality: no `docker-compose.yml` exists, Ollama is not containerized, and models must be pulled manually. For the target user (non-technical PM), this is a dead end.

**Fix**: Ollama must be a service in `docker-compose.yml` with automatic model pull on first run. Zero manual steps. The promise must be literally true.

---

## B02 — Phase Sequencing Buries the Differentiators

**Severity**: High
**Status**: Partially addressed — conflict resolution moved to Phase 2 (was Phase 4 originally)

Phase 1 MVP has no conflict resolution and no role-awareness — the two things that make NEXUS different from generic RAG. An early evaluator will try the MVP, compare it to "ChatGPT with my PDFs," and leave before seeing the differentiated features.

**Fix**: Add at minimum a basic conflict flag in Phase 1 (show both sources when similarity is high and authority levels differ). Full TRUSTED/SUPERSEDED labeling in Phase 2.

---

## B03 — WhatsApp Staleness UX

**Severity**: Medium
**Status**: Design specified — not yet implemented

No live WhatsApp integration. Users export manually. Without good UX, this feels like constant maintenance work.

**Fix**: Incremental re-ingestion (hash-based, new messages only). Ingestion status showing "last updated X hours ago." Notification when ingestion completes. PM uploads the file — the system handles the rest invisibly.

---

## B04 — Authority Hierarchy Is Hardcoded in README

**Severity**: Medium
**Status**: Fixed in decisions — configurable per project (see [decisions.md D07](../decisions.md))

The README presents a single global authority hierarchy as if it applies to all organizations. Safety-critical EPC firms have different authority structures. The configuration must be per project.

---

## B05 — No Competitor Positioning in the Pitch

**Severity**: Medium
**Status**: Addressed in [market.md](../business/market.md) — not yet in README

Notion AI, Microsoft Copilot, Confluence AI, and custom GPT wrappers all do document Q&A. The README ignores this. The pitch must explicitly state why NEXUS beats these for the target user.

**Fix**: Add a comparison table to README or marketing materials. Core argument: air-gapped + WhatsApp-native + conflict resolution + EPC-specific. See [market.md — Competitive Landscape](../business/market.md).

---

## B06 — Digital Product Model Has Structural Weaknesses

**Severity**: High
**Status**: Addressed — annual license recommended (see [business/model.md](../business/model.md))

Selling as a one-time digital download creates a revenue cliff, has no clean answer for updates, and the product complexity doesn't match the "download and use" expectation of digital product buyers.

**Fix**: Annual license key model. Client pays yearly, gets updates during that period, keeps working on their version if they don't renew. See full analysis in [business/model.md](../business/model.md).

---

## B07 — Buyer Persona Mismatch

**Severity**: Medium
**Status**: Open — see [open-questions.md Q5](../open-questions.md)

EPC firms in SEA buy software through company procurement (invoice + transfer), not personal credit cards. A "Buy Now" digital product page targets the wrong purchasing flow.

**Fix**: Design for invoice-based sales. Build an invoice template. WhatsApp-friendly sales flow. Demo before purchase.

---

## B08 — White-label Was Phase 4 — Revenue Multiplier Deferred Too Long

**Severity**: Low
**Status**: Kept in Phase 4 for now

If reselling to multiple engineering firms is the commercial play, white-label (client's logo on the UI) is what makes the product sellable to firms that won't put a third-party brand in front of their team.

**Consideration**: Move to Phase 3 if first clients request it. It is a configurable logo/color scheme change, not a major architectural investment.

---

## Related

- [technical.md](./technical.md)
- [../business/model.md](../business/model.md)
- [../business/market.md](../business/market.md)
- [../open-questions.md](../open-questions.md)
