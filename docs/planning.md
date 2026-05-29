# NEXUS — Product Planning & Design Notes

> Live document. Updated as decisions are made. Open questions tracked at the bottom.
> Last updated: 2026-05-29

---

## What We Know (Decided)

| Question | Answer |
|----------|--------|
| Who runs it today? | Power user (the builder) |
| Target operator later | Non-technical PM, onboarded with minimal setup |
| Deployment model | Self-hosted: client runs on their own VPS |
| Distribution model | Digital product — sold as a deployable package |
| First users | Builder + PMs managing 5–10 field engineers below them |
| Projects per PM | Many concurrent projects |
| WhatsApp staleness threshold | Daily is fine. 2+ days = the team is behind, not the tool |
| Primary market | SEA — Indonesia, Malaysia, Philippines focus |
| Pricing | Decide after MVP is built |
| Version support policy | TBD — latest-only vs N-1 |

---

## Open Questions (Not Yet Answered)

1. **WhatsApp language?**
   Bahasa Indonesia, English, or mixed code-switching?
   > Determines embedding model. `nomic-embed-text` is English-first and degrades on Bahasa. `multilingual-e5-large` is the proposed swap. Confirm before building the ingestion pipeline.

2. **Distribution format?**
   What does the buyer actually receive on purchase?
   - Option A: Zip file with Docker Compose bundle + license key
   - Option B: Access to a private Docker Hub image (pulled via license-authenticated registry)
   - Option C: Access to a private GitHub repo (client runs `git clone`)
   > Determines how you control updates and prevent unauthorized sharing.

3. **One-time or annual license?**
   - One-time: client pays once, owns that version forever
   - Annual: client pays yearly, gets all updates and support during that period; keeps working after lapse but gets no new versions
   > Annual is recommended (see Business Model section). Confirm before setting a price.

4. **Setup service included?**
   Do you (or someone) do the first VPS deployment for the client, or is it fully self-serve?
   > A paid "done-for-you setup" add-on removes the biggest adoption barrier and justifies a higher base price.

5. **Who is the actual buyer?**
   The PM personally (personal credit card / bank transfer), or their company (invoice + procurement department)?
   > In SEA EPC context this is almost always the company. Changes payment flow, invoicing, and sales process entirely.

---

## Business Model — Digital Product Critique

### What was decided

Sell NEXUS as a digital product: client pays → receives a deployable Docker package → runs it on their own VPS. No SaaS, no consulting, no ongoing hosting responsibility.

### Why self-hosted is correct

SaaS means owning client uptime. One crash, one memory leak, one bad deployment — and product development stops while you firefight. At solo-founder stage that kills momentum faster than anything. Self-hosted shifts responsibility cleanly: the client owns their VPS, you own the software.

**The blame doesn't disappear — it changes form.** Instead of "your service is down," you get "my update broke something." But it loses urgency and you're no longer on-call. Mitigate it with:

- One-command update: `docker-compose pull && docker-compose up -d`
- `/health` endpoint for client self-diagnosis
- Clear license boundary: *"NEXUS is the software. The VPS is yours."*
- Versioned releases with changelogs

### Where "digital product" breaks down

**Problem 1: The product complexity doesn't match the format's expectations.**
A digital product implies: download, open, use. Notion templates, Figma kits, Excel dashboards. NEXUS requires Docker, a VPS, environment config, model pulls, JWT secrets, and ongoing ingestion habits. Buyers who expect a "download and it works" experience will be frustrated and ask for refunds or support you didn't promise.

**Problem 2: One-time pricing for ongoing-development software is a trap.**
- Month 1 launch: sell 10 licenses
- Month 6: existing clients happy, no new marketing push, revenue drops near zero
- You are still building features, fixing bugs, handling questions
- You are doing ongoing work for a one-time fee

**Problem 3: Updates have no clean answer under one-time pricing.**
- Free updates forever → you've devalued all future work
- Pay again for major versions → clients feel cheated for buying early
- "Upgrade fee" → awkward conversation every release

**Problem 4: Your buyer doesn't shop this way.**
A PM at an EPC firm in Indonesia does not buy software by clicking "Buy Now" and downloading a zip. They buy through a demo, a Zoom call, an invoice to their accounts department, and a WhatsApp follow-up. The sales process will be relationship-driven regardless of how you package the product.

**Problem 5: License enforcement is trivial to bypass without infrastructure.**
Once someone has the Docker image, a zip download link can be forwarded. Without a license check mechanism, one purchase can become unlimited installs across a firm or between firms.

### Recommended model: Annual license key

Not a "subscription" (that word carries psychological baggage in the SMB market). A **renewable license**:

- Client pays (e.g., Rp 3–5 juta or regional equivalent) → receives a license key valid for 12 months
- License key enables the product and unlocks updates for that period
- After 12 months: pay to renew → continue getting updates and support
- If they don't renew: product keeps working on the version they have, no new features or fixes
- New version ships → existing clients have a clear reason to renew

**Why this works:**
- Recurring revenue (renewal cohort grows over time)
- No "subscription" framing — it's a license, not a service
- Clean update model — updates are included in the license period
- No hostage dynamic — non-renewing clients aren't cut off, just frozen in place
- Clients who try to share the key expose themselves (one key, one active installation)

**Tiering to consider later (not now):**
- Solo PM license: 1 installation, up to 3 projects
- Team license: 1 installation, unlimited projects
- Agency license: up to 5 installations (for integrators deploying for multiple clients)

---

## Architecture Implications

### Self-hosted package model

You are shipping a **deployable package**, not running infra. Consequences:

- `docker-compose up` must work first time, every time — zero manual steps
- JWT secret generated per-installation (no central auth server)
- No central observability — local logging must be sufficient for self-diagnosis
- Data never leaves client's VPS — **core sales argument for SEA enterprise clients**
- License key check must be local (no phone-home) or phone-home to a lightweight activation server
- Update path must be defined and frictionless before v1.1

**Version fragmentation risk**: clients will run different versions. Decide and document the support policy before first paid client: "latest version only" is recommended — it forces a good update experience rather than maintaining multiple versions.

### Many projects per PM → project switcher is Phase 1

A PM running 8 concurrent projects who can't switch contexts in the chat UI won't use the product. ChromaDB collections (one per project) and the project switcher component must be in Phase 1, not Phase 3.

### SEA market → multilingual gap in current tech stack

`nomic-embed-text` is English-first. EPC teams in Indonesia code-switch between Bahasa Indonesia and English mid-sentence in WhatsApp. Retrieval quality degrades significantly on Bahasa text.

**Recommended swaps (model config change, not architecture change):**

| Component | Current (README) | Proposed | Reason |
|-----------|-----------------|----------|--------|
| Embedding | `nomic-embed-text` | `multilingual-e5-large` | Handles Bahasa Indonesia properly |
| LLM | `Hermes3` | `Qwen2.5-7B` | Better multilingual SEA performance, same VRAM |

Both run via Ollama. Swap confirmed after WhatsApp language question is answered.

### 5–10 users, many projects → low concurrent query load

Peak load: ~20–50 queries/day per deployment. A 16GB VPS running Qwen2.5-7B Q4_K_M handles this. GPU not required for Phase 1. With an async query UX (user asks → gets notified when answer is ready), 30–60s CPU inference is acceptable and keeps client VPS cost low.

---

## Recommended VPS for SEA Clients

| Provider | Region | Spec | Cost/mo | Best for |
|----------|--------|------|---------|----------|
| DigitalOcean | Singapore | 16GB RAM, 8 vCPU | ~$96 | Most PM-friendly dashboard, easiest to provision |
| Vultr | Singapore | 16GB RAM, 6 vCPU | ~$80 | Budget-conscious |
| IDCloudHost | Jakarta | 16GB RAM | ~Rp 600K | Indonesian data residency requirement |
| Biznet Metro | Jakarta | Configurable | ~Rp 800K+ | Enterprise Indonesian clients |

**Official supported spec**: DigitalOcean Singapore 16GB Droplet. Document this in the setup guide as the reference deployment.

---

## Critique — Business Pain Points

### 1. "One docker-compose up" is a lie until it isn't

The README promises one-command startup but currently requires pre-pulling Ollama models manually, has no `docker-compose.yml`, and assumes Docker is pre-installed. The promise is right — it should work that way — but it must actually work. Ollama must be containerized with automatic model pull on first run. No manual steps.

### 2. Phase sequencing buries the differentiators

Phase 1 MVP has no conflict resolution and no role-awareness — the two things that distinguish NEXUS from "ChatGPT but for your documents." An early evaluator will compare it to generic RAG and leave before seeing the differentiated features. Move basic conflict resolution (flag contradictions, show both sources) into Phase 1 even in minimal form.

### 3. WhatsApp staleness UX must be invisible

No live WhatsApp integration exists — users must manually export and re-ingest. Make this feel like a non-event:
- User uploads `.txt` export via UI
- System detects file hash change, incrementally re-ingests only new messages
- Notification: "47 new decisions indexed from Project Alpha chat"
- Old chunks versioned, not deleted

### 4. Authority hierarchy must be configurable, not hardcoded

The 5-level hierarchy (ECO > vendor datasheet > SOP > WhatsApp > drafts) is stated as fixed. In safety-critical EPC work, a field technician's on-site WhatsApp message about a hazard may override a SOP. Different organizations have different authority structures. This must be configurable per project by the PM admin.

### 5. No competitor positioning in the pitch

Notion AI, Microsoft Copilot (SharePoint/Teams), and Confluence + LLM plugins all do document Q&A. The README doesn't acknowledge this. The differentiators are real (offline, conflict resolution, WhatsApp-aware, role-aware, EPC-specific) but they need to be stated explicitly against alternatives, not just described in isolation.

---

## Critique — Technical Pain Points

### 1. P&ID tag extraction is Phase 4 but is a core query type

For EPC teams, "what is the spec for AT-201?" is one of the most common questions. The MVP without tag extraction can't answer it. Move basic regex-based tag extraction (AT-201, FT-101, PV-305 patterns) to Phase 1.

### 2. "No hallucination without a source" is overclaimed

RAG reduces hallucination, it doesn't eliminate it. Qwen2.5-7B will still confabulate when retrieved context is ambiguous. The confidence signal must be defined explicitly (cosine similarity of top-k chunks, LLM self-assessment, or citation coverage ratio) and displayed in the UI. For safety-critical environments this is not a nice-to-have.

### 3. Chunking strategy is ~40% of the ingestion work

`chunker.py` is listed but never described. Naive chunking breaks table rows mid-row, splits SOP steps mid-instruction, severs BOM line items from their column headers. Every parser needs a document-type-specific chunking strategy. This is not a detail — it directly determines retrieval quality.

### 4. Multi-tenancy must be Day 1 architecture

"Project-scoped context isolation" is currently Phase 3. But ChromaDB collection naming, JWT claim scopes, and API routing must be designed for multi-tenancy from the start or Phase 3 becomes a full rewrite.
- One ChromaDB collection per project
- JWT carries `project_id` + `role` claims
- All queries scoped to `project_id`

### 5. ChromaDB has no backup strategy

If the Docker volume is lost, the entire knowledge base requires full re-ingestion. For teams with months of ingested context this is a business-continuity failure. Define: named volume mounts, daily snapshot script, export format for portability.

### 6. WhatsApp export format is fragile

iOS vs Android exports differ in date format, author display format, encoding, and media attachment handling. WhatsApp changes export format without notice. `whatsapp_parser.py` needs multi-format support and graceful fallback with clear error messages per format variant.

---

## Revised Roadmap

### Phase 1 — Working MVP

- [ ] WhatsApp `.txt` parser (multi-format: iOS + Android, Bahasa-aware)
- [ ] PDF + Excel + DOCX ingestion with document-type-aware chunking
- [ ] Basic P&ID instrument tag extraction (regex: AT-201, FT-101, PV-305 patterns)
- [ ] ChromaDB with one collection per project (multi-tenancy schema from day 1)
- [ ] Ollama + Qwen2.5-7B + multilingual-e5-large embeddings
- [ ] FastAPI with JWT auth (`project_id` + `role` in every token)
- [ ] React chat UI: source citation panel + **project switcher**
- [ ] Incremental WhatsApp re-ingestion (file hash detection, new messages only)
- [ ] Docker Compose: includes Ollama, pulls models on first run, zero manual steps
- [ ] Named volume mounts + daily ChromaDB snapshot script
- [ ] `.env.example` with all required config documented
- [ ] Setup guide targeting DigitalOcean Singapore 16GB as reference spec

### Phase 2 — Conflict Resolution

- [ ] Authority level metadata system (configurable per project by PM)
- [ ] Conflict detection between chunks on the same topic
- [ ] TRUSTED / SUPERSEDED labeling in responses
- [ ] Document version tracking
- [ ] Confidence signal defined and displayed (cosine similarity of top-k retrieved chunks)

### Phase 3 — Roles & Intent

- [ ] User roles: PM, Field Technician, Procurement, Engineer
- [ ] Intent classifier per role (same question → different answer facets)
- [ ] Admin panel: user management and project config
- [ ] Async query mode with notification (expected UX for CPU-only 30–60s inference)

### Phase 4 — Commercial Layer

- [ ] License key mechanism (annual, per-installation)
- [ ] Update delivery path (defined, documented, one-command)
- [ ] White-label support (logo, color scheme, custom domain)
- [ ] PM usage dashboard (queries/day, documents indexed, staleness alerts)
- [ ] Node-RED flow ingestion
- [ ] Advanced P&ID parsing (OCR-based, beyond regex)

---

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Deployment model | Self-hosted Docker Compose package | Client data stays on their VPS; core SEA sales argument; no on-call burden |
| Business model | Annual license key (not one-time, not SaaS) | Recurring revenue; clean update model; no hostage dynamic |
| Multi-tenancy scope | One ChromaDB collection per project | Simplest isolation, no cross-project bleed, day 1 design |
| JWT claims | Must carry `project_id` + `role` | Required for isolation and intent-aware retrieval |
| WhatsApp update model | Incremental upload via UI | Daily manual export acceptable; hash-based dedup makes it low-friction |
| Authority hierarchy | Configurable per project, not global | Orgs differ; safety-critical contexts may invert default hierarchy |
| Chunking approach | Document-type-specific per parser | Naive chunking breaks structured engineering data |
| LLM | Qwen2.5-7B (replaces Hermes3) | Better multilingual SEA performance (Bahasa/Malay/English mix) |
| Embedding model | multilingual-e5-large (replaces nomic-embed-text) | nomic degrades badly on Bahasa Indonesia |
| Project switcher | Phase 1 (moved from Phase 3) | Many-projects-per-PM is a day 1 requirement |
| Reference deployment spec | DigitalOcean Singapore 16GB | Documented as official supported spec for SEA clients |
| Version support policy | Latest-only (recommended, not yet confirmed) | Forces good update UX; avoids multi-version maintenance |
| P&ID tag extraction | Phase 1 (regex-based, moved from Phase 4) | Core query type for EPC teams; can't wait |
