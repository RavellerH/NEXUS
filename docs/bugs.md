---
id: bugs
type: tracker
status: active
last_updated: 2026-05-29
related:
  - ./todo.md
  - ./INDEX.md
  - ./open-questions.md
---

# Bug & Issue Tracker

> Log all bugs, unexpected behaviors, and technical issues here.
> For missing features or planned work, use [todo.md](./todo.md).
> For design questions, use [open-questions.md](./open-questions.md).

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `open` | Confirmed, not yet fixed |
| `in-progress` | Being actively worked on |
| `fixed` | Resolved — version noted |
| `wont-fix` | Acknowledged, not fixing (with reason) |
| `needs-repro` | Reported but not yet confirmed |

## Severity Legend

| Severity | Meaning |
|----------|---------|
| `critical` | Data loss, security issue, or system down |
| `high` | Core feature broken or unusable |
| `medium` | Feature partially broken, workaround exists |
| `low` | Minor UX issue or cosmetic |

---

## Bug Template

When logging a new bug, copy this template:

```
## BUG-XXX — [Short title]

**Status**: open | in-progress | fixed | wont-fix | needs-repro
**Severity**: critical | high | medium | low
**Phase**: 1 | 2 | 3 | 4
**Module**: [link to relevant module spec]
**Reported**: YYYY-MM-DD
**Fixed in**: vX.X (if resolved)

### Description
What is broken.

### Steps to Reproduce
1. ...
2. ...
3. ...

### Expected
What should happen.

### Actual
What actually happens.

### Notes
Any context, suspected cause, or attempted fixes.
```

---

## Known Pre-Implementation Issues

> These are design-level issues identified before any code was written.
> They are not bugs yet, but will become bugs if not addressed in implementation.

### PRE-001 — WhatsApp Parser Format Fragility

**Status**: open
**Severity**: high
**Phase**: 1
**Module**: [whatsapp-parser.md](./modules/ingestion/whatsapp-parser.md)
**Reported**: 2026-05-29

#### Description
WhatsApp `.txt` export format differs between iOS and Android, varies by locale and OS version, and changes without notice from WhatsApp. A single parser written against one format will silently fail or produce malformed chunks on other formats.

#### Expected
Parser handles all common iOS and Android export formats gracefully. On unknown format, fails loudly with a clear error message, not silently.

#### Notes
iOS format uses `[DD/MM/YYYY, HH:MM:SS]` with square brackets. Android uses `DD/MM/YYYY, HH:MM - `. Date separator, author separator, and media attachment text all vary. Need format auto-detection at parse time.

---

### PRE-002 — Embedding Dimension Lock-in

**Status**: open
**Severity**: critical
**Phase**: 1
**Module**: [vector-store.md](./modules/context-store/vector-store.md)
**Reported**: 2026-05-29

#### Description
ChromaDB collections are locked to the embedding dimension they were created with. If the embedding model is changed after documents are already ingested, the collection must be deleted and all documents re-ingested. This is not communicated to the user.

#### Expected
`.env` specifies the embedding model. Setup guide warns clearly that changing the embedding model requires full re-ingestion. The system checks at startup that the configured model matches the dimension of existing collections.

#### Notes
`multilingual-e5-large` uses 1024 dimensions. `nomic-embed-text` uses 768. These are incompatible. Decided on `multilingual-e5-large` from day 1 to avoid migration.

---

### PRE-003 — Docker Volume Loss = Total Knowledge Base Loss

**Status**: open
**Severity**: critical
**Phase**: 1
**Module**: [vector-store.md](./modules/context-store/vector-store.md)
**Reported**: 2026-05-29

#### Description
If the Docker volume containing ChromaDB data is lost (accidental `docker-compose down -v`, host disk failure, VPS rebuild), all ingested knowledge is permanently gone. There is no backup or restore mechanism.

#### Expected
Daily automated snapshot of ChromaDB data directory. Clear restore documentation. Named volumes in `docker-compose.yml` to prevent accidental deletion.

#### Notes
Snapshot can be a simple `tar` of the ChromaDB data directory, stored in a separate volume or object storage. Restore is untar + restart.

---

## Active Bugs

*No active bugs. Implementation has not started.*

---

## Resolved Bugs

*No resolved bugs yet.*
