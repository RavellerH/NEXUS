# NEXUS — Product Planning & Design Notes

> Live document. Updated as decisions are made. Open questions tracked at the bottom.

---

## What We Know (Decided)

| Question | Answer |
|----------|--------|
| Who runs it today? | Power user (the builder) |
| Target operator later | Non-technical PM, onboarded with minimal setup |
| Business model | Paid product — self-hosted package sold to clients |
| First user | Builder + PMs managing technical teams below them |
| WhatsApp staleness threshold | Daily is fine. 2+ days = the team is behind, not the tool |
| Deployment model | Self-hosted: client runs on their own VPS |
| Team size per PM | 5–10 field engineers |
| Projects per PM | Many concurrent projects |
| Primary market | SEA (Indonesia, Malaysia, Philippines focus) |
| Pricing | Decide after MVP is built |

---

## Open Questions (Blocking Architecture Decisions)

These must be answered before finalizing the system design:

1. **Language of WhatsApp chats?**
   Bahasa Indonesia, English, or mixed code-switching?
   > Determines embedding model. nomic-embed-text is English-first and degrades on Bahasa. multilingual-e5-large or paraphrase-multilingual-mpnet-base-v2 would serve SEA teams better.

2. **License enforcement mechanism?**
   Time-limited license key file, phone-home activation, or trust-based (no enforcement for now)?
   > Self-hosted means clients have the Docker image. Without enforcement, sharing is trivial.

3. **Update delivery method?**
   How do clients get v1.1 when you ship it?
   - Option A: `git pull && docker-compose pull` (requires git on server)
   - Option B: Download new release zip from a URL
   - Option C: Automatic on container restart (pull policy in docker-compose)
   > Determines whether you need a release/download infrastructure from day 1.

3. **Projects per PM?**
   One big long-running project, or multiple concurrent projects?
   > Affects ChromaDB collection design and project-switching UX.

4. **Primary market?**
   Indonesian / SEA market? (Inferred from WhatsApp-heavy EPC/IoT context.)
   > Affects pricing (Rupiah), data residency concerns, and latency to EU servers.

5. **Target price point?**
   Rough ballpark per PM per month?
   > Determines how much infra cost you can absorb per client and what tier of GPU makes sense.

---

## Architecture Implications (From Decisions Made)

### Why self-hosted (the business rationale)

SaaS means owning client uptime. One crash, one data migration gone wrong, one memory leak — and product development stops while you firefight. At solo-founder stage, that kills momentum.

Self-hosted shifts responsibility: the client owns their VPS, you own the software. The blame doesn't disappear — it changes form from "your service is down" to "my update broke something" — but it loses urgency and doesn't require you to be on-call.

**The mitigation for shifted blame:**
- Update must be one command: `docker-compose pull && docker-compose up -d`
- `/health` endpoint for self-diagnosis
- Explicit support boundary in license: *"NEXUS is the software. The VPS is yours."*
- Versioned releases with changelogs — clients choose when to update
- Policy decision needed: support latest version only, or maintain N-1?

**Version fragmentation risk**: clients will be on different versions. Decide before v1.1: is "update to get support" the policy? If yes, the update process must be frictionless enough that clients actually do it.

### Self-hosted changes everything

You are shipping a **deployable package**, not running infra. Consequences:

- `docker-compose up` must work first time, every time — no manual steps
- JWT secret is generated per-installation (not from a central auth server)
- No central observability — local logging must be good enough for PM to self-diagnose
- Data never leaves client's VPS — this is the **core sales argument** for SEA enterprise
- You need a license key mechanism before first paid client
- You need an update path before v1.1

### Many projects per PM → Project switcher is Phase 1, not Phase 3

A PM running 8 concurrent projects who can't switch between them in the chat UI won't use the product. ChromaDB collections (one per project) and a project switcher component move to Phase 1.

### SEA market → Multilingual gap in current tech stack

`nomic-embed-text` is English-first. EPC teams in Indonesia code-switch between Bahasa Indonesia and English mid-sentence in WhatsApp. Retrieval quality degrades on Bahasa.

**Recommended swaps:**
- Embedding: `nomic-embed-text` → `multilingual-e5-large` or `paraphrase-multilingual-mpnet-base-v2`
- LLM: `Hermes3` → `Qwen2.5-7B` (better multilingual performance across SEA languages, similar VRAM)

Both run via Ollama. This is a model config change, not an architecture change.

### Recommended VPS for SEA clients

| Provider | Region | Spec | Cost/mo | Best for |
|----------|--------|------|---------|----------|
| DigitalOcean | Singapore | 16GB RAM, 8 vCPU | ~$96 | Most PM-friendly dashboard |
| Vultr | Singapore | 16GB RAM, 6 vCPU | ~$80 | Budget-conscious |
| IDCloudHost | Jakarta | 16GB RAM | ~Rp 600K | Indonesian data residency |
| Biznet Metro | Jakarta | Configurable | ~Rp 800K+ | Enterprise Indonesian clients |

**Default recommendation**: DigitalOcean Singapore 16GB Droplet. Document this as the official supported spec.

### 5–10 users, many projects → Low concurrent query load

Peak load: ~20–50 queries/day per deployment. A single 16GB VPS running Qwen2.5-7B Q4_K_M can handle this. GPU is not required for Phase 1. If response time is acceptable at 30–60s (async notification UX), CPU-only is viable and keeps client infrastructure cost low.

---

## Critique — Business Pain Points

### 1. "One docker-compose up" is aspirational, not real
The current README promises one-command startup but requires pre-pulling Ollama models manually, no docker-compose.yml exists yet, and the target users (EPC teams, HSE compliance) are not DevOps users. Someone must own infrastructure. Define who that person is per deployment before designing the onboarding flow.

### 2. Phase sequencing buries the differentiators
Phase 1 MVP has no conflict resolution and no role-awareness — the two things that make NEXUS different from "just plug docs into ChatGPT." An early evaluator will compare it to generic RAG and leave before seeing what's unique. **Consider moving basic conflict resolution into Phase 1** even in a minimal form (flag contradictions, don't resolve them automatically).

### 3. WhatsApp as a knowledge source will always be stale without a clear UX
No live WhatsApp integration exists. Users must manually export and re-ingest. The system needs to make this feel invisible:
- User uploads `.txt` export via UI (or drops in a folder)
- System detects hash change, incrementally re-ingests only new messages
- Notification: "47 new decisions indexed from Project Alpha chat"
- Old chunks are versioned, not deleted

### 4. Authority hierarchy is rigid; real organizations differ
The current hierarchy (ECO > vendor datasheet > SOP > WhatsApp > drafts) is hardcoded. In safety-critical EPC work, a field tech's on-site WhatsApp message about a hazard may override a SOP. Authority levels must be **configurable per project** by the PM admin, not hardcoded globally.

### 5. No competitor acknowledgment in the pitch
Notion AI, Microsoft Copilot (SharePoint/Teams), Confluence + LLM are all doing document Q&A. The README doesn't position against them. The real differentiators — offline, conflict resolution, WhatsApp, role-aware, EPC-specific — need to be explicit in the pitch.

### 6. White-label is Phase 4 but is a revenue multiplier
If the business model is consulting/licensing to engineering firms, white-label is not a nice-to-have — it's what makes the product sellable to firms that won't put an unknown brand in front of their clients. Consider moving it earlier.

---

## Critique — Technical Pain Points

### 1. P&ID instrument tag extraction is Phase 4, should be Phase 1
For EPC teams, "what is the spec for AT-201?" is a primary query. The MVP without tag extraction from P&IDs doesn't serve the core user's most common question. Even basic regex-based tag extraction (AT-201, FT-101, PV-305) in Phase 1 would close this gap.

### 2. "No hallucination without a source" is overclaimed
RAG reduces hallucination, it doesn't eliminate it. Hermes3 at 7B will still confabulate when retrieved context is ambiguous. The confidence signal must be defined explicitly: cosine similarity of the top-k retrieved chunks, LLM self-assessment score, or citation coverage ratio. For safety-critical environments this is not optional.

### 3. Hermes3 7B will struggle with dense engineering data
Tables, BOMs, P&ID tag lists, and procurement specs are structured data, not prose. A 7B model without fine-tuning has poor structured data recall. The tech stack should either note that model choice is configurable, or plan a structured data extraction layer separate from the LLM.

### 4. Chunking strategy is the core work, not a detail
`chunker.py` is listed but never described. For engineering documents, naive chunking breaks table rows mid-row, splits SOP steps mid-instruction, and severs BOM line items from column headers. Each parser needs a document-type-specific chunking strategy. This is approximately 40% of the ingestion work.

### 5. Multi-tenancy must be Day 1 architecture
"Project-scoped context isolation" is Phase 3. But ChromaDB collection naming, JWT claim scopes, and API routing must be designed for multi-tenancy from the start or Phase 3 becomes a full rewrite. Design: one ChromaDB collection per project, JWT carries `project_id` and `role` claims, all queries are scoped to `project_id`.

### 6. ChromaDB has no stated persistence or backup strategy
If the Docker volume is lost, the entire knowledge base requires full re-ingestion. For engineering teams with months of ingested context this is a business-continuity failure. Define: volume mount paths, daily snapshot to object storage (S3-compatible), export format for portability.

### 7. WhatsApp export format is fragile
iOS vs Android exports differ in date format, author display name format, encoding, and media attachment handling. WhatsApp changes export format without notice. `whatsapp_parser.py` needs multi-format support and graceful fallback with clear error messages.

### 8. Quick Start will fail for any first-time user
The current README Quick Start (`docker-compose up -d && open localhost:3000`) requires:
- `docker-compose.yml` (doesn't exist yet)
- Ollama pre-installed and running (not in Docker Compose)
- `hermes3` and `nomic-embed-text` already pulled
Fix: either include Ollama in Docker Compose with model pull on first run, or rewrite the Quick Start to be honest about prerequisites.

---

## Infrastructure Options

### Context
- Core heavy component: Ollama + Hermes3 7B (~5GB RAM for Q4_K_M quantized)
- Everything else (FastAPI, ChromaDB, React) is lightweight
- Bottleneck is inference latency, not storage or compute for the rest

### Option A — Single VPS, CPU-only

**Target**: Hetzner CPX41 (~€20/mo) or DigitalOcean 16GB (~$96/mo)

| Spec | Value |
|------|-------|
| CPU | 8 cores |
| RAM | 16GB |
| Model | Hermes3 Q4_K_M (~5GB RAM) |
| Response time | 30–90 seconds per query |
| Cost | ~€20–96/mo |

**Verdict**: Workable for power user / internal demo. Too slow for a product people pay for. Acceptable for async workflows (user asks, gets notified when answer is ready).

### Option B — VPS + GPU inference (recommended)

Split services: cheap persistent VPS for app + database, GPU instance for inference.

| GPU Option | Cost | VRAM | Response time |
|------------|------|------|---------------|
| RunPod RTX 3090 (on-demand) | ~$0.44/hr | 24GB | 2–5s |
| Lambda Labs A10G (on-demand) | ~$0.60/hr | 24GB | 2–5s |
| Vast.ai community GPUs | ~$0.20–0.40/hr | varies | 3–8s |
| Hetzner GPU A40 (dedicated) | ~€250/mo | 48GB | 1–3s |

**Architecture**: Hetzner CPX21 (€5/mo) for FastAPI + ChromaDB + React. Separate GPU endpoint for Ollama inference. At low usage, on-demand GPU is cheapest. Above ~100 queries/day, reserved GPU pays off.

### Option C — Managed SaaS (target end state)

You host everything. Each client = isolated project namespace in shared infrastructure.

```
Single GPU server
  ├── Ollama (shared, queued requests)
  ├── FastAPI (multi-tenant, JWT-scoped)
  └── ChromaDB (one collection per project)

Thin VPS per region (optional, for latency)
```

Charge per project/month. You absorb infra cost, which is ~$50–150/mo per GPU instance serving multiple clients. At 10 clients paying $50/mo each = $500/mo revenue, $150/mo infra = viable.

### Recommended path

1. **Now**: Single Hetzner VPS (16GB RAM, €20/mo), CPU inference, async response UX. Use this to validate the product with your first real PM + team.
2. **First paying client**: Add a RunPod on-demand GPU endpoint. Keep VPS for everything else.
3. **At 3–5 clients**: Evaluate dedicated GPU vs. shared on-demand based on actual query volume.
4. **Scale**: Multi-tenant SaaS with one or two GPU instances serving all clients.

---

## Revised Roadmap (Proposed)

### Phase 1 — Working MVP
- [ ] WhatsApp `.txt` parser (multi-format: iOS + Android, Bahasa-aware)
- [ ] PDF + Excel + DOCX ingestion with document-type-aware chunking
- [ ] Basic P&ID instrument tag extraction (regex-based: AT-201, FT-101 patterns)
- [ ] ChromaDB with project-scoped collections (one collection per project — multi-tenancy from day 1)
- [ ] Ollama + Qwen2.5-7B (multilingual, better for SEA) + multilingual-e5-large embeddings
- [ ] FastAPI with JWT auth (carries `project_id` + `role` claims)
- [ ] React chat UI with source citation panel **and project switcher**
- [ ] Incremental WhatsApp re-ingestion (hash-based, new messages only)
- [ ] Docker Compose (includes Ollama, pulls models on first run, no manual steps)
- [ ] Volume-mounted ChromaDB with daily snapshot script
- [ ] `.env.example` with all required config documented
- [ ] Setup guide targeting DigitalOcean Singapore 16GB as reference spec

### Phase 2 — Conflict Resolution
- [ ] Authority level metadata system (configurable per project by PM, not global)
- [ ] Conflict detection between chunks (same topic, different claim)
- [ ] TRUSTED / SUPERSEDED labeling in responses
- [ ] Document version tracking
- [ ] Confidence signal: defined as cosine similarity of top-k retrieved chunks, displayed in UI

### Phase 3 — Roles & Intent
- [ ] User roles: PM, Field Technician, Procurement, Engineer
- [ ] Intent classifier per role (same question → different answer facets)
- [ ] Admin panel for users and projects
- [ ] Async query mode with notification (for CPU-only deployments where 30–60s response is expected)

### Phase 4 — Commercial Layer
- [ ] License key mechanism (time-limited file or activation)
- [ ] Update delivery path (defined and documented)
- [ ] White-label support (logo, color scheme, domain)
- [ ] Usage dashboard for PM (queries/day, documents indexed, staleness alerts)
- [ ] Node-RED flow ingestion
- [ ] Advanced P&ID parsing (beyond regex, OCR-based)

---

## Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Deployment model | Self-hosted Docker Compose package | Client data stays on their VPS; core SEA sales argument |
| Multi-tenancy scope | ChromaDB collection per project | Simplest isolation, no cross-project bleed |
| JWT claims | Must carry `project_id` + `role` | Required for both isolation and intent-aware retrieval |
| WhatsApp update model | Incremental via UI upload | Daily manual export is acceptable; hash-based dedup makes it low-friction |
| Authority hierarchy | Configurable per project, not global | Different orgs have different authority structures |
| Chunking approach | Document-type-specific per parser | Naive chunking breaks structured engineering data |
| LLM choice | Qwen2.5-7B (replacing Hermes3) | Better multilingual performance for SEA (Bahasa Indonesia, Malay, English mix) |
| Embedding model | multilingual-e5-large (replacing nomic-embed-text) | nomic-embed-text is English-first; degrades on Bahasa |
| Project switcher | Phase 1 (moved from Phase 3) | PMs managing many projects need it from day 1 |
| Reference deployment spec | DigitalOcean Singapore 16GB | Documented as official supported spec for SEA clients |

---

*Last updated: 2026-05-29. Questions answered by: builder (Farhan Budiman).*
