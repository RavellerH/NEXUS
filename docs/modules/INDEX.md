---
id: modules-index
type: navigation
status: active
last_updated: 2026-05-29
related:
  - ../INDEX.md
  - ../decisions.md
  - ../todo.md
---

# Modules — System Architecture

> All NEXUS backend modules. Start here to understand the system design before implementing any component.

---

## System Data Flow

```mermaid
graph LR
    subgraph Ingestion
        DOC["📄 Documents\n(WhatsApp, PDF, Excel,\nDOCX, P&ID)"]
        PARSE["Parsers"]
        CHUNK["Chunker\n(type-specific)"]
        META["Metadata Tagger\n(source, authority,\nproject_id, timestamp)"]
        EMBED["Embedder\n(multilingual-e5-large)"]
    end

    subgraph Context Store
        VS["Vector Store\n(ChromaDB)\none collection per project"]
        AR["Authority Ranker"]
        CR["Conflict Resolver"]
    end

    subgraph Query Pipeline
        Q["User Query"]
        ID["Intent Detector\n(role-aware)"]
        QE["Query Engine\n(semantic + tag search)"]
        RB["Response Builder\n(LLM + citations)"]
        ANS["Answer\n+ TRUSTED/SUPERSEDED\n+ Sources"]
    end

    DOC --> PARSE --> CHUNK --> META --> EMBED --> VS
    Q --> ID --> QE --> VS
    VS --> AR --> CR --> RB
    RB --> ANS
```

---

## Module Map

### Ingestion Layer

| Module | File | Status | Phase |
|--------|------|--------|-------|
| WhatsApp Parser | [ingestion/whatsapp-parser.md](./ingestion/whatsapp-parser.md) | Spec only | 1 |
| PDF Parser | [ingestion/pdf-parser.md](./ingestion/pdf-parser.md) | Spec only | 1 |
| Excel Parser | [ingestion/excel-parser.md](./ingestion/excel-parser.md) | Spec only | 1 |
| DOCX Parser | [ingestion/docx-parser.md](./ingestion/docx-parser.md) | Spec only | 1 |
| P&ID Parser | [ingestion/pid-parser.md](./ingestion/pid-parser.md) | Spec only | 1 |

### Context Store Layer

| Module | File | Status | Phase |
|--------|------|--------|-------|
| Vector Store | [context-store/vector-store.md](./context-store/vector-store.md) | Spec only | 1 |
| Conflict Resolver | [context-store/conflict-resolver.md](./context-store/conflict-resolver.md) | Spec only | 2 |
| Authority Ranker | [context-store/authority-ranker.md](./context-store/authority-ranker.md) | Spec only | 2 |

### Query Layer

| Module | File | Status | Phase |
|--------|------|--------|-------|
| Intent Detector | [query/intent-detector.md](./query/intent-detector.md) | Spec only | 3 |
| Query Engine | [query/query-engine.md](./query/query-engine.md) | Spec only | 1 |
| Response Builder | [query/response-builder.md](./query/response-builder.md) | Spec only | 1 |

### API Layer

| Module | File | Status | Phase |
|--------|------|--------|-------|
| API Routes | [api/api.md](./api/api.md) | Spec only | 1 |

---

## Module Dependency Graph

```mermaid
graph TD
    WA[whatsapp-parser] --> PIPE[ingestion-pipeline]
    PDF[pdf-parser] --> PIPE
    XL[excel-parser] --> PIPE
    DOCX[docx-parser] --> PIPE
    PID[pid-parser] --> PIPE

    PIPE --> META[metadata-tagger]
    META --> VS[vector-store]

    VS --> QE[query-engine]
    VS --> AR[authority-ranker]
    AR --> CR[conflict-resolver]

    QE --> RB[response-builder]
    CR --> RB

    ID[intent-detector] --> QE

    API[api-routes] --> QE
    API --> PIPE
    API --> ID
```

---

## Tech Stack Reference

| Component | Technology | Notes |
|-----------|-----------|-------|
| Backend framework | FastAPI (Python) | Async, OpenAPI auto-docs |
| Vector database | ChromaDB | Local, embedded, one collection per project |
| LLM | Qwen2.5-7B via Ollama | ~5GB RAM Q4_K_M; configurable via `.env` |
| Embeddings | multilingual-e5-large via Ollama | 1024 dimensions; handles Bahasa + English |
| Ingestion framework | LlamaIndex (optional) or custom pipeline | TBD based on flexibility needs |
| PDF extraction | PyMuPDF | Text + table extraction |
| Frontend | React + Tailwind CSS | |
| Auth | JWT (PyJWT) | Claims: `project_id`, `role`, `user_id`, `exp` |
| Deployment | Docker Compose | All services containerized |
