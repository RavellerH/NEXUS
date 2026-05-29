# NEXUS

> **Self-hosted AI context engine for engineering project teams in Southeast Asia.**
> Ingest WhatsApp exports, PDFs, Excel BOMs, SOPs, and P&IDs — get trusted, conflict-resolved, role-aware answers. No cloud. No data leaks. Runs on your own VPS.

---

## The Problem

Engineering project knowledge is scattered across:
- WhatsApp group chats (where 80% of real decisions happen)
- PDF vendor datasheets and manuals
- Excel BOMs and procurement sheets
- Word SOPs and site meeting minutes
- P&ID drawings with instrument tags (AT-201, FT-101, PV-305)

When a new team member joins, context dies. When two documents contradict each other, nobody knows which to trust. When a project gets handed over, institutional knowledge walks out the door.

**NEXUS fixes this.**

---

## How It Works

```
Ingest your docs → Context Store → Ask a question → Trusted Answer + Sources
      |                  |                                      |
 WhatsApp            ChromaDB                       Cites document, page,
 PDFs, Excel      + Conflict Resolver               date, authority level,
 SOPs, P&IDs      + Authority Ranker                TRUSTED / SUPERSEDED
```

### 3 Core Capabilities

**1. Conflict Resolution Engine**
Every document gets an authority level. When two sources contradict each other, both are shown — one labeled `TRUSTED`, the other `SUPERSEDED`. Nothing is hidden.

```
Authority Hierarchy (configurable per project):
  Level 1 — Signed Engineering Change Orders (ECO)
  Level 2 — Approved vendor datasheets
  Level 3 — Internal SOPs (latest version)
  Level 4 — WhatsApp decisions (timestamped, from project lead)
  Level 5 — Drafts and old revisions
```

**2. Intent-Aware Retrieval**
Same question, different role = different answer facet.
- Procurement engineer asks about a cable spec → part number, vendor, price, lead time
- Field technician asks the same → diameter, insulation type, hazard zone rating
- Project manager asks → budget line, approval status, ETA

**3. Source Citation with Confidence**
Every answer cites exactly which document, which page, and which date. Answers include a confidence indicator based on source similarity. When context is insufficient, NEXUS says so — it does not guess.

---

## Knowledge Sources Supported

| Source | Format | Notes |
|--------|--------|-------|
| WhatsApp group exports | `.txt` | iOS + Android format support, Bahasa-aware |
| PDF datasheets & manuals | `.pdf` | Table + text extraction via PyMuPDF |
| Excel / Google Sheets BOMs | `.xlsx` | Row-aware with column header context |
| Word documents / SOPs | `.docx` | Section-aware, numbered step preservation |
| P&ID drawings | `.pdf` | Instrument tag extraction (AT-201, FT-101) |
| Node-RED flows | `.json` | Natural language description of flows *(Phase 4)* |
| Email threads | `.eml` | Thread-aware chunking *(Backlog)* |

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | Python + FastAPI | Async, JWT auth |
| Vector DB | ChromaDB | Local, one collection per project |
| LLM | Ollama + Qwen2.5-7B | Multilingual SEA support (Bahasa + English) |
| Embeddings | multilingual-e5-large | 1024-dim; handles Bahasa Indonesia natively |
| Ingestion | Custom parsers + LlamaIndex | Document-type-specific chunking |
| Frontend | React + Tailwind CSS | Project switcher, source citation panel |
| Auth | JWT | `project_id` + `role` claims per token |
| Deployment | Docker Compose | All services containerized, models auto-pulled |

---

## Target Users

**Primary market: Indonesia, Malaysia, Philippines**

| User | How they use NEXUS |
|------|-------------------|
| **Project Manager** | Uploads documents, manages projects and team members, asks high-level status questions |
| **Field Technician** | Asks about equipment specs, installation procedures, hazard zones |
| **Procurement Engineer** | Asks about BOMs, vendor options, pricing, lead times |
| **Site / Design Engineer** | Asks about technical specs, standards, calculations |

Built for EPC (Engineering, Procurement, Construction) teams, industrial IoT integrators, and HSE compliance teams.

---

## Project Structure

```
nexus/
├── backend/
│   ├── ingestion/
│   │   ├── parsers/
│   │   │   ├── whatsapp_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── excel_parser.py
│   │   │   ├── docx_parser.py
│   │   │   └── pid_parser.py
│   │   ├── chunker.py
│   │   ├── metadata_tagger.py
│   │   └── ingestion_pipeline.py
│   ├── context_store/
│   │   ├── vector_store.py
│   │   ├── conflict_resolver.py
│   │   └── authority_ranker.py
│   ├── query/
│   │   ├── intent_detector.py
│   │   ├── query_engine.py
│   │   └── response_builder.py
│   ├── api/
│   │   ├── routes/
│   │   └── main.py
│   └── models/
│       └── schemas.py
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatInterface.jsx
│       │   ├── SourcePanel.jsx
│       │   ├── ProjectSwitcher.jsx
│       │   └── UploadZone.jsx
│       └── pages/
├── docs/                    ← Full architecture and planning documentation
│   ├── INDEX.md             ← Start here
│   ├── decisions.md
│   ├── open-questions.md
│   ├── todo.md
│   ├── bugs.md
│   ├── modules/
│   ├── business/
│   └── critique/
├── docker-compose.yml
└── README.md
```

---

## Roadmap

### Phase 1 — Working MVP
- [ ] WhatsApp `.txt` parser (iOS + Android, Bahasa-aware)
- [ ] PDF + Excel + DOCX ingestion with document-type-aware chunking
- [ ] P&ID instrument tag extraction (AT-201, FT-101 — regex-based)
- [ ] ChromaDB with project-scoped collections (one per project)
- [ ] Ollama + Qwen2.5-7B + multilingual-e5-large
- [ ] FastAPI with JWT auth (`project_id` + `role` per token)
- [ ] React chat UI with source panel and **project switcher**
- [ ] Incremental WhatsApp re-ingestion (hash-based, new messages only)
- [ ] Docker Compose (all services, models pulled on first run)
- [ ] Daily ChromaDB snapshot + restore documentation
- [ ] Setup guide for DigitalOcean Singapore 16GB

### Phase 2 — Conflict Resolution
- [ ] Authority level metadata (configurable per project by PM)
- [ ] Conflict detection between retrieved chunks
- [ ] TRUSTED / SUPERSEDED labels in responses
- [ ] Document version tracking
- [ ] Confidence signal displayed per answer

### Phase 3 — Roles & Intent
- [ ] User roles: PM, Field Technician, Procurement, Engineer
- [ ] Intent classifier — same question, role-specific answer facets
- [ ] Admin panel for users and project configuration
- [ ] Async query mode with notification (for CPU-only inference wait times)

### Phase 4 — Commercial Layer
- [ ] Annual license key mechanism
- [ ] One-command update delivery (`docker-compose pull && docker-compose up -d`)
- [ ] White-label support (logo, color scheme, custom domain)
- [ ] PM usage dashboard (queries/day, staleness alerts, ingestion status)
- [ ] Node-RED flow ingestion
- [ ] OCR-based P&ID parsing for scanned drawings

---

## Deployment

NEXUS runs on a VPS you own or rent. **Reference spec**: DigitalOcean Singapore, 16GB RAM, 8 vCPU (~$96/mo).

```bash
# Clone the repo
git clone https://github.com/RavellerH/NEXUS.git
cd NEXUS

# Configure environment
cp .env.example .env
# Edit .env — set JWT_SECRET and other required values

# Start all services (downloads models on first run — ~5GB, takes ~10 minutes)
docker-compose up -d

# Open the UI
open http://localhost:3000
```

> **Status**: Implementation not started. The `docker-compose.yml` and application code are in development. The Quick Start above reflects the intended first-run experience once Phase 1 is complete.

---

## Documentation

Full architecture, design decisions, module specs, and planning docs live in [`docs/`](./docs/).

| Document | Contents |
|----------|----------|
| [`docs/INDEX.md`](./docs/INDEX.md) | System map — start here |
| [`docs/decisions.md`](./docs/decisions.md) | All locked design decisions with rationale |
| [`docs/open-questions.md`](./docs/open-questions.md) | Unresolved questions blocking design |
| [`docs/todo.md`](./docs/todo.md) | All tasks organized by phase |
| [`docs/modules/INDEX.md`](./docs/modules/INDEX.md) | Module architecture and data flow |
| [`docs/business/market.md`](./docs/business/market.md) | SEA market context and target users |

---

## Why Not Just Use [Existing Tool]?

| Tool | Why it falls short for EPC teams |
|------|----------------------------------|
| Notion AI / Confluence AI | Cloud — data leaves your network; no WhatsApp ingestion; no conflict resolution |
| Microsoft Copilot | Requires M365 ecosystem; cloud; expensive per-seat pricing |
| Custom ChatGPT wrapper | Data sent to OpenAI; no conflict resolution; no role-aware answers |
| Generic RAG (build yourself) | Requires an engineering team to build and maintain indefinitely |

NEXUS is the only tool designed specifically for EPC teams in SEA: air-gapped, WhatsApp-native, conflict-resolving, and role-aware.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

*Built for engineering teams that live in WhatsApp and die by scattered docs.*
