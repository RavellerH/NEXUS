---
id: todo
type: tracker
status: active
last_updated: 2026-05-29
related:
  - ./INDEX.md
  - ./bugs.md
  - ./decisions.md
  - ./modules/INDEX.md
---

# Master To-Do List

> All implementation tasks organized by phase.
> For bugs and issues found during implementation, log them in [bugs.md](./bugs.md).
> For design questions that arise, log them in [open-questions.md](./open-questions.md).

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Done |
| `[!]` | Blocked — see open-questions.md |
| `[-]` | Deferred or cancelled |

---

## Phase 1 — Working MVP

> Goal: A working local deployment that a power user can use on a real project.
> Success: PM can upload docs, ask questions, get cited answers, switch between projects.

### Infrastructure & DevOps

- [ ] `docker-compose.yml` — includes all services: FastAPI, ChromaDB, Ollama, React
- [ ] Ollama service with automatic model pull on first run (`qwen2.5:7b` + `multilingual-e5-large`)
- [ ] Named Docker volumes for ChromaDB persistence
- [ ] `.env.example` with all required variables documented
- [ ] Daily ChromaDB snapshot script (cron job or container sidecar)
- [ ] `/health` endpoint on FastAPI returning service status
- [ ] Setup guide for DigitalOcean Singapore 16GB Droplet (step-by-step, terminal commands)

### Backend — Ingestion

- [ ] `whatsapp_parser.py` — iOS + Android format support, Bahasa-aware, date/author extraction
  - See spec: [modules/ingestion/whatsapp-parser.md](./modules/ingestion/whatsapp-parser.md)
- [ ] `pdf_parser.py` — text extraction via PyMuPDF, table extraction, section-aware chunking
  - See spec: [modules/ingestion/pdf-parser.md](./modules/ingestion/pdf-parser.md)
- [ ] `excel_parser.py` — row-aware chunking with column headers prepended
  - See spec: [modules/ingestion/excel-parser.md](./modules/ingestion/excel-parser.md)
- [ ] `docx_parser.py` — section-aware parsing, numbered step preservation
  - See spec: [modules/ingestion/docx-parser.md](./modules/ingestion/docx-parser.md)
- [ ] `pid_parser.py` — basic regex tag extraction (AT-201, FT-101, PV-305 patterns)
  - See spec: [modules/ingestion/pid-parser.md](./modules/ingestion/pid-parser.md)
- [ ] `metadata_tagger.py` — assigns source type, authority level (default), project_id, timestamp
- [ ] `ingestion_pipeline.py` — orchestrates parsers, chunker, embedder, ChromaDB write
- [ ] Incremental re-ingestion: file hash detection, skip unchanged files, only process new content
- [ ] Ingestion status API: returns progress, errors, chunk count per document

### Backend — Context Store

- [ ] `vector_store.py` — ChromaDB wrapper, collection-per-project, CRUD for chunks
  - See spec: [modules/context-store/vector-store.md](./modules/context-store/vector-store.md)
- [ ] Collection naming: `nexus_project_{project_id}`
- [ ] Embedding via `multilingual-e5-large` — dimension must be set consistently

### Backend — Query

- [ ] `query_engine.py` — semantic search against active project collection
  - See spec: [modules/query/query-engine.md](./modules/query/query-engine.md)
- [ ] Tag-based retrieval for instrument tags (complements semantic search)
- [ ] `response_builder.py` — formats LLM answer + source citations
  - See spec: [modules/query/response-builder.md](./modules/query/response-builder.md)

### Backend — API

- [ ] `main.py` — FastAPI app setup, middleware, CORS
- [ ] Auth routes: login, token refresh, JWT issue with `project_id` + `role`
- [ ] Ingestion routes: upload document, trigger re-ingest, ingestion status
- [ ] Query routes: submit query, get answer + sources
- [ ] Project routes: create, list, switch active project
- [ ] User routes: create user, assign role
  - See spec: [modules/api/api.md](./modules/api/api.md)
- [ ] `schemas.py` — Pydantic models for all request/response bodies

### Frontend

- [ ] Project switcher component — dropdown or sidebar, updates active `project_id` in session
- [ ] Chat interface — query input, streaming or polling response display
- [ ] Source citation panel — shows document, page/line, date, authority level for each source
- [ ] Upload zone — drag-and-drop or file picker for all supported document types
- [ ] Ingestion status indicator — shows progress or last-indexed timestamp
- [ ] Login screen — JWT-based auth

---

## Phase 2 — Conflict Resolution

> Goal: NEXUS can detect when two sources contradict each other and surface both with authority labels.
> Success: A query that returns conflicting specs shows TRUSTED and SUPERSEDED labels with sources.

- [ ] Authority level metadata field on every chunk (default hierarchy from D07)
- [ ] PM admin UI: configure authority hierarchy per project
- [ ] `authority_ranker.py` — assigns authority score to each retrieved chunk
  - See spec: [modules/context-store/authority-ranker.md](./modules/context-store/authority-ranker.md)
- [ ] `conflict_resolver.py` — detects chunks with contradictory claims on the same topic
  - See spec: [modules/context-store/conflict-resolver.md](./modules/context-store/conflict-resolver.md)
- [ ] TRUSTED / SUPERSEDED labels in response output
- [ ] Document version tracking — detect when a newer version of a document supersedes an older one
- [ ] Confidence signal: cosine similarity of top-k chunks, displayed alongside each source

---

## Phase 3 — Roles & Intent

> Goal: Same question from different roles returns different facets of the answer.
> Success: Procurement engineer gets part number + lead time; field tech gets diameter + hazard rating.

- [ ] `intent_detector.py` — classifies query intent based on user role and query text
  - See spec: [modules/query/intent-detector.md](./modules/query/intent-detector.md)
- [ ] Role-specific retrieval: query engine passes role context to retrieval and response building
- [ ] Admin panel: user management (create, assign role, deactivate)
- [ ] Admin panel: project management (create, configure authority hierarchy, manage members)
- [ ] Async query mode: user submits query, gets notified when answer is ready (for slow CPU inference)

---

## Phase 4 — Commercial Layer

> Goal: NEXUS is ready to sell as a packaged annual license product.

- [ ] License key mechanism: annual time-limited key, per-installation
  - Approach: license file checked at startup; key tied to installation fingerprint or trusted on honor
- [ ] Update delivery: one-command update (`docker-compose pull && docker-compose up -d`)
- [ ] Changelog: versioned release notes, client-readable
- [ ] White-label: configurable logo, color scheme, custom domain via `.env`
- [ ] PM usage dashboard: queries/day, documents indexed, last ingestion timestamp, staleness alert
- [ ] Multi-project dashboard: overview of all projects and their status
- [ ] Node-RED flow ingestion: `.json` flow files → natural language description chunks
- [ ] Advanced P&ID parsing: OCR-based tag extraction for scanned P&IDs

---

## Backlog (No Phase Assigned)

- [ ] Email thread ingestion (`.eml` format, thread-aware chunking)
- [ ] Slack export ingestion (similar structure to WhatsApp)
- [ ] API documentation (OpenAPI/Swagger auto-generated)
- [ ] Backup restore tooling: restore ChromaDB snapshot from object storage
- [ ] Multi-language UI (Bahasa Indonesia translation)

---

## Completed

*Nothing yet — implementation has not started.*
