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

## Persistence

- ChromaDB data directory: `/app/data/chromadb/` (inside container)
- Docker volume mount: `nexus_chromadb:/app/data/chromadb`
- Named volume prevents accidental deletion on `docker-compose down`

**Snapshot**: daily cron job tars `/app/data/chromadb/` to `/app/data/backups/chromadb_YYYY-MM-DD.tar.gz`

See [bugs.md PRE-002](../../bugs.md) (dimension lock-in) and [PRE-003](../../bugs.md) (volume loss risk).

---

## Related

- [conflict-resolver.md](./conflict-resolver.md)
- [authority-ranker.md](./authority-ranker.md)
- [../query/query-engine.md](../query/query-engine.md)
- [../../decisions.md → D04, D05](../../decisions.md)
