---
id: whatsapp-parser
type: spec
status: not-implemented
phase: 1
last_updated: 2026-05-29
related:
  - ../INDEX.md
  - ../../decisions.md#d11
  - ../../bugs.md#pre-001
  - ../../todo.md
---

# Module: WhatsApp Parser

> `backend/ingestion/parsers/whatsapp_parser.py`

---

## Purpose

Parse WhatsApp `.txt` export files into structured chunks with author, timestamp, and message content. Handle format differences between iOS and Android exports. Support incremental re-ingestion (new messages only).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Path to `.txt` WhatsApp export |
| `project_id` | `str` | Project this chat belongs to |
| `authority_level` | `int` | Default: 4 (WhatsApp from project lead) |
| `last_ingested_ts` | `datetime \| None` | For incremental mode: skip messages before this timestamp |

---

## Outputs

List of `Chunk` objects:

```python
@dataclass
class Chunk:
    content: str           # Message text
    author: str            # Display name from export
    timestamp: datetime    # Parsed message timestamp
    source_file: str       # Original filename
    source_type: str       # "whatsapp"
    project_id: str
    authority_level: int
    chunk_id: str          # SHA256 of content + timestamp
```

---

## Format Support

### iOS format
```
[DD/MM/YYYY, HH:MM:SS] Author Name: Message text
[15/03/2024, 09:42:11] Budi Santoso: Sudah confirm dengan vendor
```

### Android format
```
DD/MM/YYYY, HH:MM - Author Name: Message text
15/03/2024, 09:42 - Budi Santoso: Sudah confirm dengan vendor
```

### Detection strategy
Auto-detect format at parse time by checking the first 5 lines. Raise a clear `UnsupportedFormatError` if neither pattern matches — do not silently produce empty or malformed chunks.

---

## Chunking Strategy

Per [decisions.md D11](../../decisions.md): each WhatsApp message = one chunk.

**Grouping heuristic** (optional, Phase 2): Messages within a 30-minute window from the same author on the same topic may be merged into one chunk for better context. Phase 1: one message = one chunk.

**System messages** (media omitted, missed voice call, etc.): Skip these. Do not ingest non-content lines.

---

## Incremental Re-ingestion

1. Caller passes `last_ingested_ts`
2. Parser skips all messages with `timestamp <= last_ingested_ts`
3. Returns only new messages as chunks
4. Caller is responsible for storing the new `last_ingested_ts` after successful ingestion

---

## Known Issues

- See [bugs.md PRE-001](../../bugs.md#pre-001) — format fragility across iOS/Android versions
- WhatsApp changes export format without notice; maintain a format version registry
- Author display names are not unique identifiers — two people with the same display name will be indistinguishable

---

## Related

- [pdf-parser.md](./pdf-parser.md)
- [../../decisions.md → D11](../../decisions.md)
- [../../bugs.md → PRE-001](../../bugs.md)
- [../../todo.md → Phase 1](../../todo.md)
