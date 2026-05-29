---
id: decisions
type: log
status: active
last_updated: 2026-05-29
related:
  - ./open-questions.md
  - ./INDEX.md
  - ./planning.md
---

# Decision Log

> All locked design and product decisions with full rationale.
> When an open question is answered, add it here and mark it resolved in [open-questions.md](./open-questions.md).

---

## D01 — Deployment Model: Self-Hosted Docker Compose

**Status**: Locked
**Date**: 2026-05-29
**Phase**: All

### Decision
NEXUS is a self-hosted product. Clients deploy and run it on their own VPS using Docker Compose. The builder does not manage client infrastructure.

### Rationale
SaaS means owning client uptime. One crash or bad deployment stops product development while the builder firefights. At solo-founder stage this kills momentum. Self-hosted shifts infra responsibility to the client. The blame changes form ("my update broke") but loses urgency and removes on-call burden.

### Constraints introduced
- `docker-compose up` must work first time, every time — no manual steps
- JWT secret generated per-installation (no central auth server)
- License enforcement must work without a persistent central server, or use a lightweight activation endpoint
- Update delivery must be defined before v1.1

### Related
- [business/model.md](./business/model.md)
- [business/infrastructure.md](./business/infrastructure.md)
- [open-questions.md → Q2](./open-questions.md)

---

## D02 — Business Model: Annual License Key

**Status**: Recommended — pending builder confirmation
**Date**: 2026-05-29
**Phase**: 4 (commercial layer)

### Decision
NEXUS is sold as an annual renewable license, not a one-time purchase and not a monthly SaaS subscription.

### How it works
- Client pays → receives license key valid for 12 months
- Key enables the product and authorizes updates for that period
- After 12 months: renew to continue receiving updates and support
- Non-renewing clients keep the product working on the version they have — no forced cutoff

### Rationale
One-time pricing creates a revenue cliff and has no clean answer for how updates are delivered or charged. Monthly subscription ("SaaS") has the connotation of ongoing service the builder doesn't want to commit to. Annual license is a renewable software license — common in the B2B software market, expected by company procurement departments, and creates a renewal cohort that grows over time.

### Tiering (future)
- Solo PM license: 1 installation, up to 3 projects
- Team license: 1 installation, unlimited projects
- Agency license: up to 5 installations

### Related
- [business/model.md](./business/model.md)
- [open-questions.md → Q3](./open-questions.md)
- [critique/business.md](./critique/business.md)

---

## D03 — LLM: Qwen2.5-7B (replacing Hermes3)

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1

### Decision
Use Qwen2.5-7B via Ollama instead of Hermes3.

### Rationale
Hermes3 is English-first. SEA EPC teams in Indonesia and Malaysia code-switch between Bahasa Indonesia and English in WhatsApp and other documents. Qwen2.5-7B has significantly better multilingual performance across SEA languages with similar VRAM requirements (~5GB Q4_K_M quantized). Both run via Ollama with no architecture change required.

### Constraints
- Pending confirmation via Q1 (WhatsApp language) — if English-only, Hermes3 would have been fine, but the swap is low-risk either way
- Model must be configurable in `.env` so clients can swap to a different Ollama model

### Related
- [modules/query/query-engine.md](./modules/query/query-engine.md)
- [open-questions.md → Q1](./open-questions.md)
- [business/market.md](./business/market.md)

---

## D04 — Embedding Model: multilingual-e5-large (replacing nomic-embed-text)

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1

### Decision
Use `multilingual-e5-large` for embeddings instead of `nomic-embed-text`.

### Rationale
`nomic-embed-text` is English-first and degrades on Bahasa Indonesia text. WhatsApp chats — the most critical knowledge source — will be written in Bahasa or mixed language. Poor embedding quality at ingestion time means poor retrieval quality at query time. `multilingual-e5-large` handles Bahasa Indonesia, Malay, Filipino, and English with equal quality. Embedding dimension changes from 768 (nomic) to 1024 (e5-large) — this must be set consistently from day 1 since ChromaDB collections are dimension-locked.

### Constraints
- Embedding model must be set in `.env` and consistent across all ingestion and query operations
- Once a ChromaDB collection is created with a given dimension, it cannot be changed without re-ingesting
- Document this clearly in setup guide

### Related
- [modules/context-store/vector-store.md](./modules/context-store/vector-store.md)
- [modules/ingestion/whatsapp-parser.md](./modules/ingestion/whatsapp-parser.md)
- [open-questions.md → Q1](./open-questions.md)

---

## D05 — Multi-tenancy: One ChromaDB Collection Per Project

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1 (design), grows in Phase 3

### Decision
Each project gets its own named ChromaDB collection. All queries are scoped to the active `project_id`. No cross-project retrieval.

### Rationale
This is the simplest isolation model. Alternatives (filtering by metadata within a shared collection, separate ChromaDB instances) add complexity without benefit at this scale. One collection per project means no risk of cross-project bleed and no complex filter logic in every query.

### Collection naming convention
`nexus_project_{project_id}` — e.g., `nexus_project_42`

### Constraints
- `project_id` must be in every JWT token
- All API routes must validate `project_id` from the JWT before any ChromaDB operation
- Project deletion must drop the entire collection (with confirmation)

### Related
- [modules/context-store/vector-store.md](./modules/context-store/vector-store.md)
- [modules/api/api.md](./modules/api/api.md)

---

## D06 — JWT Auth: project_id + role Claims

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1

### Decision
Every JWT token issued by NEXUS carries two custom claims: `project_id` (string) and `role` (enum: `pm` | `engineer` | `field_tech` | `procurement`).

### Rationale
`project_id` is required for D05 (collection scoping). `role` is required for intent-aware retrieval (Phase 3) but must be in the token schema from day 1 to avoid token schema migration later. Default role for Phase 1: `pm` for admin users, `engineer` for everyone else.

### Related
- [modules/api/api.md](./modules/api/api.md)
- [modules/query/intent-detector.md](./modules/query/intent-detector.md)

---

## D07 — Authority Hierarchy: Configurable Per Project

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 2

### Decision
Authority levels are not globally hardcoded. The PM admin configures authority levels per project via the admin panel.

### Default hierarchy (if not configured)
1. Signed Engineering Change Orders (ECO)
2. Approved vendor datasheets
3. Internal SOPs (latest version)
4. WhatsApp decisions (timestamped, from project lead)
5. Drafts and old revisions

### Rationale
The README hardcodes a single authority hierarchy, but real EPC organizations differ. In safety-critical contexts, a field technician's on-site WhatsApp hazard report may override a SOP. The hierarchy must be editable per project.

### Related
- [modules/context-store/authority-ranker.md](./modules/context-store/authority-ranker.md)
- [modules/context-store/conflict-resolver.md](./modules/context-store/conflict-resolver.md)

---

## D08 — Project Switcher: Phase 1 (moved from Phase 3)

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1

### Decision
The project switcher UI component is a Phase 1 requirement, not Phase 3.

### Rationale
The target user (PM managing many concurrent projects) needs to switch project context in the chat UI from day 1. A PM running 8 concurrent projects with no switcher will not use the product. The ChromaDB collection-per-project design (D05) makes this straightforward: switching projects just changes the active `project_id` in the session.

### Related
- [modules/api/api.md](./modules/api/api.md)
- [todo.md → Phase 1](./todo.md)

---

## D09 — P&ID Tag Extraction: Phase 1 (moved from Phase 4)

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1

### Decision
Basic P&ID instrument tag extraction (regex-based) moves to Phase 1. Advanced OCR-based parsing remains Phase 4.

### Rationale
"What is the spec for AT-201?" is one of the most common EPC team queries. The MVP without tag extraction cannot answer it. Regex patterns for common tag formats (AT-201, FT-101, PV-305, TT-101, etc.) cover 80% of cases and can be implemented in hours, not days.

### Implementation
- Regex during PDF ingestion: `[A-Z]{2,4}-\d{3,4}` as a baseline
- Extract tags into metadata field on each chunk
- Enable tag-based retrieval alongside semantic retrieval

### Related
- [modules/ingestion/pid-parser.md](./modules/ingestion/pid-parser.md)
- [modules/query/query-engine.md](./modules/query/query-engine.md)

---

## D10 — Reference Deployment Spec: DigitalOcean Singapore 16GB

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1

### Decision
The official documented and supported deployment spec is DigitalOcean Singapore, 16GB RAM, 8 vCPU Droplet.

### Rationale
- Low latency for SEA clients
- PM-friendly dashboard (easiest for non-technical users to manage billing and basic ops)
- 16GB RAM fits Qwen2.5-7B Q4_K_M (~5GB) + ChromaDB + FastAPI + React with headroom
- ~$96/mo is within budget for a business-critical tool for an EPC PM

### Related
- [business/infrastructure.md](./business/infrastructure.md)

---

## D11 — Chunking: Document-Type-Specific Per Parser

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1

### Decision
Each parser implements its own chunking strategy appropriate to the document type. No shared naive chunker.

### Rationale
Naive sentence or fixed-size chunking breaks table rows mid-row, splits SOP steps mid-instruction, and severs BOM line items from their column headers. Poor chunking directly causes poor retrieval quality regardless of embedding model quality.

### Per-type strategy
| Document type | Chunking approach |
|--------------|------------------|
| WhatsApp | By message, grouped by date window or topic thread |
| PDF (text) | By paragraph, respecting section headers |
| PDF (P&ID) | By instrument tag region; whole tag block as one chunk |
| Excel BOM | By row, with column headers prepended to each row chunk |
| DOCX SOP | By section heading, preserving numbered steps as units |
| Email thread | By message, preserving reply context |

### Related
- [modules/ingestion/whatsapp-parser.md](./modules/ingestion/whatsapp-parser.md)
- [modules/ingestion/pdf-parser.md](./modules/ingestion/pdf-parser.md)
- [modules/ingestion/excel-parser.md](./modules/ingestion/excel-parser.md)
- [modules/ingestion/docx-parser.md](./modules/ingestion/docx-parser.md)

---

## D12 — WhatsApp Chat Language: Multilingual Code-switching (Bahasa Indonesia & English)

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1

### Decision
Confirm that target clients' WhatsApp project chats happen in a multilingual format with heavy code-switching between Bahasa Indonesia/Malay and English. 

### Rationale
This locks in the decision to use the `multilingual-e5-large` embedding model (D04) and ensure the `qwen2.5:7b` LLM (D03) is prompted to understand and synthesize responses across both English and local Southeast Asian dialects. The WhatsApp parser will be written to support this multilingual content from day 1, avoiding subsequent parsing or embedding dimension migrations.

### Related
- [open-questions.md → Resolved Questions](./open-questions.md)
- [decisions.md → D03, D04](./decisions.md)
- [modules/ingestion/whatsapp-parser.md](./modules/ingestion/whatsapp-parser.md)

---

## D13 — Distribution Format: Zip File / Private GitHub Repo

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 1 & 4

### Decision
NEXUS will be distributed via a private GitHub repository for developers and early clients (Phase 1), and as a downloadable ZIP package containing `docker-compose.yml` and default configurations. Private Docker Hub image delivery with automated license checks is deferred to Phase 4.

### Rationale
Using a zip archive and private GitHub repository minimizes launch and infrastructure overhead for early-stage clients while facilitating extremely rapid update iteration during Phase 1. It allows trust-based adoption initially, with technical IP protection and programmatic validation layers planned for the Phase 4 commercialization push.

### Related
- [open-questions.md → Resolved Questions](./open-questions.md)
- [business/model.md](./business/model.md)
- [todo.md → Phase 4](./todo.md)

---

## D14 — License Pricing Model: Recurring Annual/Monthly Renewal

**Status**: Locked
**Date**: 2026-05-29
**Phase**: 4

### Decision
Lock in a recurring subscription-like license key model (with options for annual or monthly renewals) over a flat one-time purchase.

### Rationale
A recurring license model mitigates the "revenue cliff" risk, supports ongoing developer maintenance, and aligns well with standard B2B software purchasing cycles expected by company procurement departments in Southeast Asia. Active subscriptions authorize clients to pull future product updates and access support.

### Related
- [open-questions.md → Resolved Questions](./open-questions.md)
- [business/model.md](./business/model.md)
- [critique/business.md](./critique/business.md)
