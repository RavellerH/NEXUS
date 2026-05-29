---
id: critique-technical
type: narrative
status: active
last_updated: 2026-05-29
related:
  - ./business.md
  - ../modules/INDEX.md
  - ../bugs.md
  - ../decisions.md
---

# Technical Critique

> Technical pain points identified during architecture review. Each item links to the relevant decision or bug.

---

## T01 — P&ID Tag Extraction Was Phase 4 — Now Phase 1

**Severity**: High
**Status**: Fixed — moved to Phase 1 (see [decisions.md D09](../decisions.md))

"What is the spec for AT-201?" is one of the most common EPC queries. A Phase 1 MVP that cannot answer instrument tag questions does not serve the core user.

**Fix**: Regex-based tag extraction during P&ID ingestion. Pattern: `[A-Z]{1,4}-\d{3,4}[A-Z]?`. Covers 80% of ISA 5.1 standard tags. OCR-based extraction for scanned P&IDs deferred to Phase 4.

See: [modules/ingestion/pid-parser.md](../modules/ingestion/pid-parser.md)

---

## T02 — "No Hallucination Without a Source" Is Overclaimed

**Severity**: High
**Status**: Addressed — confidence signal defined in response-builder spec

RAG reduces hallucination, it does not eliminate it. Qwen2.5-7B will confabulate when retrieved context is ambiguous, incomplete, or when the query topic has no relevant chunks. Claiming "no hallucination" is dangerous in safety-critical environments.

**Fix**: 
1. Define confidence signal: mean cosine similarity of top-k retrieved chunks
2. Display confidence tier in UI: High / Medium / Low
3. Add explicit disclaimer when confidence is Low: "Limited relevant sources found. Verify this answer independently."
4. Prompt engineering: instruct the LLM to say "I don't have enough information" rather than guess

See: [modules/query/response-builder.md](../modules/query/response-builder.md)

---

## T03 — Chunking Strategy Was Unspecified — Now Defined Per Document Type

**Severity**: High
**Status**: Fixed — see [decisions.md D11](../decisions.md)

Naive fixed-size or sentence chunking breaks table rows mid-row, splits SOP steps mid-instruction, and severs BOM line items from column headers. Poor chunking directly causes poor retrieval regardless of model quality.

**Fix**: Document-type-specific chunking in every parser. Defined in [decisions.md D11](../decisions.md) and individual module specs.

---

## T04 — Multi-tenancy Was Phase 3 — Now Day 1 Architecture

**Severity**: High
**Status**: Fixed — one collection per project from Phase 1 (see [decisions.md D05](../decisions.md))

Retrofitting project isolation after the first version is a partial rewrite. ChromaDB collection naming, JWT scoping, and API route design must account for multi-tenancy from the first line of code.

**Fix**: ChromaDB collection named `nexus_project_{project_id}`. JWT carries `project_id` claim. All API routes validate `project_id` before any DB operation.

---

## T05 — ChromaDB Embedding Dimension Lock-in

**Severity**: Critical
**Status**: Open — tracked in [bugs.md PRE-002](../bugs.md)

ChromaDB collections are locked to the embedding dimension they were created with. Changing the embedding model after ingestion requires dropping and re-creating all collections. This is not communicated to users.

**Fix**: 
1. Document embedding model as a locked configuration in `.env`
2. Add startup check: verify configured model dimension matches existing collections
3. Warn clearly in setup guide: "Changing EMBEDDING_MODEL requires full re-ingestion"

---

## T06 — No Volume Persistence / Backup Strategy

**Severity**: Critical
**Status**: Partially addressed — tracked in [bugs.md PRE-003](../bugs.md)

`docker-compose down -v` or a disk failure destroys the entire knowledge base. No backup mechanism exists.

**Fix**: Named Docker volumes (prevent accidental deletion). Daily snapshot cron job. Restore documentation. See [business/infrastructure.md](../business/infrastructure.md).

---

## T07 — WhatsApp Export Format Fragility

**Severity**: High
**Status**: Open — tracked in [bugs.md PRE-001](../bugs.md)

iOS and Android export formats differ. WhatsApp changes format without notice. A parser written against one format will fail silently or produce garbage on others.

**Fix**: Format auto-detection. Loud failure on unrecognized format (not silent empty output). Format version registry to track changes over time.

See: [modules/ingestion/whatsapp-parser.md](../modules/ingestion/whatsapp-parser.md)

---

## T08 — Hermes3 Replaced by Qwen2.5-7B for Multilingual SEA Support

**Severity**: High
**Status**: Fixed — see [decisions.md D03](../decisions.md)

Hermes3 is English-first. EPC teams in Indonesia and Malaysia code-switch between Bahasa Indonesia and English. Hermes3 would produce poor answers on Bahasa-heavy WhatsApp content.

**Fix**: Qwen2.5-7B via Ollama. Similar VRAM requirements, significantly better multilingual performance.

---

## T09 — nomic-embed-text Replaced by multilingual-e5-large

**Severity**: High
**Status**: Fixed — see [decisions.md D04](../decisions.md)

`nomic-embed-text` is English-first and degrades on Bahasa Indonesia. All retrieval quality depends on embedding quality at ingestion time. Using an English-only model for SEA content produces poor semantic matches.

**Fix**: `multilingual-e5-large` (1024 dimensions). Handles Bahasa, Malay, Filipino, and English equally well.

---

## T10 — Quick Start in README Will Fail for Any First-Time User

**Severity**: Medium
**Status**: Open — blocked on docker-compose.yml creation (Phase 1 task)

```bash
docker-compose up -d
open http://localhost:3000
```

This fails because: no `docker-compose.yml`, Ollama is external, models not pulled. The Quick Start is aspirational, not functional.

**Fix**: Build the actual `docker-compose.yml` first, then rewrite the Quick Start to match reality. The promise should only be in the README once it's literally true.

---

## T11 — No Scanned PDF Support in Phase 1

**Severity**: Low
**Status**: Accepted limitation — log warning, Phase 4 adds OCR

PyMuPDF returns empty text for scanned (image-only) PDFs. Many P&IDs and older vendor documents are scanned.

**Fix**: Phase 1: detect empty extraction, log a warning with the filename, skip the file. Phase 4: add OCR via Tesseract or EasyOCR.

---

## T12 — WhatsApp Context Fragmentation & Threading Fragility

**Severity**: High
**Status**: Open
**Phase**: 1 & 2
**Module**: [whatsapp-parser.md](../modules/ingestion/whatsapp-parser.md)
**Reported**: 2026-05-29

### Description
Splitting WhatsApp message exports strictly message-by-message or using static chronological windows breaks non-linear conversation threads. In safety-critical or vendor negotiation situations, a message like "Sudah confirm, ganti tipe B" is completely stripped of context (i.e. which vendor or tag Budi was replying to) if retrieved in isolation.

### Fix
Upgrade the WhatsApp parser to utilize overlapping sliding windows of 15–20 messages during ingestion, reconstruct thread structures using reply-to references when present, and inject context-bearing global headers into every chat chunk.

---

## T13 — Dense Vector Blindness on Precise Alphanumeric Loop & Part Codes

**Severity**: High
**Status**: Open
**Phase**: 1
**Module**: [vector-store.md](../modules/context-store/vector-store.md)
**Reported**: 2026-05-29

### Description
Dense embeddings (`multilingual-e5-large`) compress semantic meaning but are notoriously poor at distinguishing between exact, alphanumeric technical identifiers (e.g. `CBL-001-HV-4` vs `CBL-001-HV-3` or `AT-201` vs `AT-202`).

### Fix
Implement a hybrid search engine combining the dense vector database with a lightweight, FTS5 full-text sparse keyword index (e.g. SQLite BM25). Integrate technical tag extraction at query time and perform Reciprocal Rank Fusion (RRF) to prioritize exact keyword matches.

---

## T14 — High CPU Query Latency from Pairwise Contradiction Analysis

**Severity**: High
**Status**: Open
**Phase**: 2
**Module**: [conflict-resolver.md](../modules/context-store/conflict-resolver.md)
**Reported**: 2026-05-29

### Description
Evaluating potential contradictions between retrieved document chunks on-the-fly using a CPU-bound 7B local LLM inside the real-time query loop introduces unacceptable latencies (exceeding several minutes).

### Fix
Shift contradiction evaluations to an asynchronous background worker triggered immediately post-ingestion. Scan high-similarity chunk clusters, pre-compute conflicts offline via the local LLM, and store flagged conflicts in a local relational table for sub-millisecond query-time lookups.

---

## T15 — Danger of Safety Information Omission via Role-Aware Intent Detection

**Severity**: High
**Status**: Open
**Phase**: 3
**Module**: [intent-detector.md](../modules/query/intent-detector.md)
**Reported**: 2026-05-29

### Description
Role-based query filtering (e.g. restricting a Procurement user's context entirely to pricing and delivery schedules) risks omitting vital technical safety alerts or standard mismatch notifications. A PM or Procurement Engineer might buy a part that is physically incompatible if safety conflicts are filtered out.

### Fix
Configure a "Global Safety Override" rule inside the intent detector. Critical safety warnings, hazardous ratings, and physical spec contradictions must bypass role filters and be surfaced regardless of user role.

---

## Related

- [business.md](./business.md)
- [../bugs.md](../bugs.md)
- [../decisions.md](../decisions.md)
- [../modules/INDEX.md](../modules/INDEX.md)
