---
id: vector-store
type: spec
status: not-implemented
phase: 1
last_updated: 2026-05-29
related:
  - ../INDEX.md
  - ./conflict-resolver.md
  - ./authority-ranker.md
  - ../../decisions.md#d05
  - ../../decisions.md#d04
  - ../../bugs.md#pre-002
  - ../../bugs.md#pre-003
---

# Module: Vector Store

> `backend/context_store/vector_store.py`

---

## Purpose

ChromaDB wrapper. Manages creation, querying, and deletion of per-project collections. All ingested chunks are stored here. All semantic queries execute against this store.

---

## Design Decisions

- **One collection per project** — see [decisions.md D05](../../decisions.md)
- **Embedding model: multilingual-e5-large** — see [decisions.md D04](../../decisions.md)
- **Embedding dimension: 1024** — fixed from day 1; cannot be changed without full re-ingestion
- **Hybrid retrieval: ChromaDB (semantic) + SQLite FTS5 (exact)** — see Hybrid Index section below

---

## Collection Naming

```
nexus_project_{project_id}
```

Examples: `nexus_project_1`, `nexus_project_42`

---

## Chunk Metadata Schema

Every chunk stored in ChromaDB carries this metadata:

```python
{
    "chunk_id": str,           # SHA256 of content + source + timestamp
    "source_file": str,        # Original filename
    "source_type": str,        # "whatsapp" | "pdf" | "excel" | "docx" | "pid" | "eml"
    "project_id": str,
    "authority_level": int,    # 1–5; lower = higher authority
    "author": str | None,      # For WhatsApp and email
    "timestamp": str,          # ISO 8601; document date or message date
    "section_title": str | None,
    "instrument_tags": list[str] | None,  # P&ID tags found in this chunk
    "ingested_at": str,        # ISO 8601; when this chunk was indexed
}
```

---

## Interface

```python
class VectorStore:
    def __init__(self, project_id: str) -> None: ...

    def upsert(self, chunks: list[Chunk]) -> None:
        """Add or update chunks. Uses chunk_id for deduplication."""

    def query(
        self,
        query_text: str,
        n_results: int = 10,
        where: dict | None = None,
    ) -> list[RetrievedChunk]: ...

    def query_by_tag(self, tag: str) -> list[RetrievedChunk]:
        """Exact match on instrument_tags metadata field."""

    def delete_by_source(self, source_file: str) -> None:
        """Remove all chunks from a specific file (for re-ingestion)."""

    def delete_collection(self) -> None:
        """Drop entire project collection. Irreversible."""

    def collection_stats(self) -> dict:
        """Returns chunk count, last ingested timestamp, source file list."""
```

---

## Hybrid Index: ChromaDB + SQLite FTS5

> **Why this matters**: Dense embeddings (`multilingual-e5-large`) compress semantic meaning but are unreliable for exact alphanumeric identifiers. `AT-201` and `AT-202` produce nearly identical embedding vectors. A query for "AT-201 pressure spec" may retrieve chunks about AT-202 with higher confidence than the correct AT-201 chunk. The same problem applies to part numbers (`CBL-001-HV-4` vs `CBL-001-HV-3`), PO numbers, and document reference codes.

### Architecture

Two parallel indexes, one query router:

```
User query
    │
    ├── Contains alphanumeric tag/code?  (regex detection)
    │       │
    │       YES → SQLite FTS5 exact search  →  100% precision results
    │       │         (instrument tags, part numbers, PO numbers)
    │       │
    │       NO  → ChromaDB semantic search  →  top-k semantic results
    │
    └── Merge + deduplicate → response builder
```

### SQLite FTS5 schema

```sql
-- One database per project: /app/data/fts/nexus_project_{project_id}.db
CREATE VIRTUAL TABLE chunks_fts USING fts5(
    chunk_id,       -- FK to ChromaDB chunk
    content,        -- Full text for FTS search
    instrument_tags,-- Space-separated tag list: "AT-201 FT-101 PV-305"
    part_numbers,   -- Extracted part/PO numbers
    source_file,
    tokenize = "unicode61 remove_diacritics 1"
);
```

### Query routing logic

```python
EXACT_PATTERN = re.compile(r'\b[A-Z]{1,4}-\d{3,4}[A-Z]?\b|\bCBL-\w+\b|\bPO-\d+\b')

def route_query(query_text: str) -> str:
    if EXACT_PATTERN.search(query_text):
        return "fts"   # precision-first
    return "semantic"  # recall-first
```

### Interface additions

```python
class VectorStore:
    # ... existing methods ...

    def fts_search(
        self,
        query_text: str,
        n_results: int = 10,
    ) -> list[RetrievedChunk]:
        """SQLite FTS5 full-text search. Used for exact alphanumeric queries."""

    def hybrid_query(
        self,
        query_text: str,
        n_results: int = 10,
    ) -> list[RetrievedChunk]:
        """Routes to FTS5 or semantic search based on query content. Preferred entry point."""
```

### Storage

- FTS5 database: `/app/data/fts/nexus_project_{project_id}.db`
- Docker volume mount: `nexus_fts:/app/data/fts`
- SQLite is included in Python stdlib — no additional service required
- FTS5 index is rebuilt from ChromaDB chunks on first run; kept in sync by `upsert()`

---

## Persistence

- ChromaDB data directory: `/app/data/chromadb/` (inside container)
- FTS5 database directory: `/app/data/fts/` (inside container)
- Docker volume mounts:
  - `nexus_chromadb:/app/data/chromadb`
  - `nexus_fts:/app/data/fts`
- Named volumes prevent accidental deletion on `docker-compose down`

**Snapshot**: daily cron job tars both `/app/data/chromadb/` and `/app/data/fts/` to `/app/data/backups/`

See [bugs.md PRE-002](../../bugs.md) (dimension lock-in) and [PRE-003](../../bugs.md) (volume loss risk).

---

## Related

- [conflict-resolver.md](./conflict-resolver.md)
- [authority-ranker.md](./authority-ranker.md)
- [../query/query-engine.md](../query/query-engine.md)
- [../../decisions.md → D04, D05](../../decisions.md)
