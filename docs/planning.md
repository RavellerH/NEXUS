---
id: planning
type: narrative
status: active
last_updated: 2026-05-29
related:
  - ./INDEX.md
  - ./decisions.md
  - ./open-questions.md
  - ./todo.md
---

# NEXUS — Planning Summary

> This is the narrative summary of all product and architecture discussions.
> For structured data (decisions, tasks, questions, module specs), use the linked files below.

**Start here if you're new**: [INDEX.md](./INDEX.md)

---

## The Product

NEXUS is a self-hosted AI context engine for engineering project teams in SEA. It ingests WhatsApp exports, PDFs, Excel BOMs, Word SOPs, and P&ID drawings — and returns trusted, conflict-resolved, role-aware answers with source citations.

Everything runs on the client's own VPS. No cloud. No data leakage. Sold as an annual license.

---

## The Problem It Solves

Engineering project knowledge lives across WhatsApp group chats, PDF vendor datasheets, Excel BOMs, Word SOPs, P&ID drawings, and email threads. When a new team member joins, context dies. When two documents contradict each other, nobody knows which to trust. When a project gets handed over, institutional knowledge walks out the door.

NEXUS fixes this for EPC teams, IoT integrators, and HSE compliance teams in Indonesia, Malaysia, and the Philippines.

---

## What Makes It Different

1. **WhatsApp as a first-class knowledge source** — most enterprise tools ignore this; EPC teams live here
2. **Conflict resolution with authority labels** — TRUSTED / SUPERSEDED instead of a hidden guess
3. **Fully air-gapped** — all data stays on the client's server; no API calls to OpenAI or Anthropic
4. **Role-aware answers** — procurement engineer and field tech get different facets from the same question

---

## Key Decisions Summary

All decisions with full rationale are in [decisions.md](./decisions.md). Short version:

| Decision | Chosen |
|----------|--------|
| Deployment | Self-hosted Docker Compose |
| Business model | Annual license key |
| LLM | Qwen2.5-7B via Ollama |
| Embedding | multilingual-e5-large (1024 dim) |
| Vector DB | ChromaDB, one collection per project |
| Auth | JWT with project_id + role claims |
| Target infra | DigitalOcean Singapore 16GB |
| Market | SEA — Indonesia, Malaysia, Philippines |

---

## Open Questions

5 questions remain unanswered. Full context: [open-questions.md](./open-questions.md)

| # | Question |
|---|----------|
| Q1 | WhatsApp language — Bahasa, English, or mixed? |
| Q2 | Distribution format — zip, Docker Hub, GitHub? |
| Q3 | One-time vs annual license confirmed? |
| Q4 | Setup service included as add-on? |
| Q5 | Buyer: PM personally or company procurement? |

---

## Roadmap Summary

Full task list: [todo.md](./todo.md)

- **Phase 1**: Working MVP — all parsers, ChromaDB, query engine, chat UI with project switcher, Docker Compose deployment
- **Phase 2**: Conflict resolution — authority hierarchy, TRUSTED/SUPERSEDED labels
- **Phase 3**: Roles & intent — role-aware answers, admin panel
- **Phase 4**: Commercial layer — license key, updates, white-label

---

## Document System

This planning doc is part of a larger linked system. Navigate via [INDEX.md](./INDEX.md).

| Need | Go to |
|------|-------|
| Understand what was decided and why | [decisions.md](./decisions.md) |
| See what's unanswered | [open-questions.md](./open-questions.md) |
| Pick up a task | [todo.md](./todo.md) |
| Log a bug | [bugs.md](./bugs.md) |
| Understand a module | [modules/INDEX.md](./modules/INDEX.md) |
| Business model detail | [business/model.md](./business/model.md) |
| Market context | [business/market.md](./business/market.md) |
| VPS / deployment | [business/infrastructure.md](./business/infrastructure.md) |
| Business pain points | [critique/business.md](./critique/business.md) |
| Technical pain points | [critique/technical.md](./critique/technical.md) |
