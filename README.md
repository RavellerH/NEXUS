# NEXUS

> **Self-hosted AI context engine for engineering project teams.**
> Ingest WhatsApp exports, PDFs, Excel BOMs, SOPs, and P&IDs — get trusted, conflict-resolved, role-aware answers. No cloud. No data leaks. One `docker-compose up`.

---

## The Problem

Engineering project knowledge is scattered across:
- WhatsApp group chats (where 80% of real decisions happen)
- PDF vendor datasheets and manuals
- Excel BOMs and procurement sheets
- Word SOPs and site meeting minutes
- P&ID drawings with instrument tags
- Emails and Node-RED flow configs

When a new team member joins, context dies. When two documents contradict each other, nobody knows which to trust. When a project gets handed over, institutional knowledge walks out the door.

**NEXUS fixes this.**

---

## How It Works

```
Ingest your docs --> Context Store --> Ask a question --> Trusted Answer + Sources
     |                    |                                        |
  WhatsApp             ChromaDB                          Cites doc, page,
  PDFs, Excel       + Conflict Resolver                  date, authority level
  SOPs, P&IDs       + Intent Detector
```

### 3 Core Innovations

**1. Conflict Resolution Engine**
Every document gets an authority level. When two sources contradict each other, the higher authority wins and both are shown — one labeled `TRUSTED`, the other `SUPERSEDED`.

```
Authority Hierarchy:
  Level 1: Signed Engineering Change Orders (ECO)
  Level 2: Approved vendor datasheets
  Level 3: Internal SOPs (latest version)
  Level 4: WhatsApp decisions (timestamped, from project lead)
  Level 5: Drafts, old revisions
```

**2. Intent-Aware Retrieval**
Same question, different role = different answer.
- Procurement engineer asks about cable spec --> gets: part number, vendor, price, lead time
- Field technician asks the same --> gets: diameter, insulation type, hazard zone rating
- Project manager asks --> gets: budget line, approval status, ETA

**3. Source Citation with Confidence**
Every answer cites exactly which document, which page, and which date. No hallucination without a source.

---

## Knowledge Sources Supported

| Source | Format | Notes |
|--------|--------|-------|
| WhatsApp group exports | `.txt` | Date-aware, author-tagged chunking |
| PDF datasheets & manuals | `.pdf` | Table + text extraction via PyMuPDF |
| Excel / Google Sheets BOMs | `.xlsx` | Row-aware with column header context |
| Word documents / SOPs | `.docx` | Section-aware parsing |
| P&ID drawings | `.pdf` | Instrument tag extraction (AT-201, FT-101) |
| Node-RED flows | `.json` | Natural language description of flows |
| Email threads | `.eml` | Thread-aware chunking |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python + FastAPI |
| Vector DB | ChromaDB (local, self-hosted) |
| LLM | Ollama + Hermes 3 |
| Embeddings | `nomic-embed-text` via Ollama |
| Ingestion | LlamaIndex |
| Frontend | React + Tailwind CSS |
| Auth | JWT (role-based) |
| Deployment | Docker Compose |

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
│   │   │   └── nodered_parser.py
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
├── docker-compose.yml
└── README.md
```

---

## Roadmap

### Phase 1 — MVP (Current)
- [ ] WhatsApp `.txt` parser
- [ ] PDF + Excel ingestion
- [ ] ChromaDB + Ollama backend
- [ ] Basic React chat UI
- [ ] Source citation in answers
- [ ] Docker Compose deployment

### Phase 2 — Conflict Resolution
- [ ] Authority level metadata system
- [ ] Conflict detection between chunks
- [ ] TRUSTED / SUPERSEDED labeling in responses
- [ ] Document version tracking

### Phase 3 — Roles & Intent
- [ ] User roles: PM, Field Technician, Procurement, Engineer
- [ ] Intent classifier per role
- [ ] Project-scoped context isolation
- [ ] Admin panel for users and projects

### Phase 4 — Advanced Ingestion
- [ ] Instrument tag extraction from P&IDs (AT-201, FT-101)
- [ ] Node-RED flow ingestion
- [ ] Multi-project dashboard
- [ ] White-label support for clients

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/RavellerH/NEXUS.git
cd NEXUS

# Start all services
docker-compose up -d

# Open the UI
open http://localhost:3000
```

> Requires: Docker, Docker Compose, and Ollama with `hermes3` and `nomic-embed-text` models pulled.

---

## Target Users

- EPC (Engineering, Procurement, Construction) project teams
- Industrial IoT integrators
- HSE and CEMS compliance teams
- Any engineering team drowning in scattered project documentation

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for engineering teams that live in WhatsApp and die by scattered docs.*
