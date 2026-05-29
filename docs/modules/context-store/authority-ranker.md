---
id: authority-ranker
type: spec
status: not-implemented
phase: 2
last_updated: 2026-05-29
related:
  - ./conflict-resolver.md
  - ./vector-store.md
  - ../../decisions.md#d07
---

# Module: Authority Ranker

> `backend/context_store/authority_ranker.py`

---

## Purpose

Re-rank retrieved chunks by authority level before passing them to the conflict resolver and response builder. Higher authority chunks rank above lower authority chunks, even if the lower authority chunk has slightly higher semantic similarity.

---

## Phase

Phase 2. In Phase 1, chunks are returned in semantic similarity order only.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `chunks` | `list[RetrievedChunk]` | Raw top-k from vector store |
| `project_id` | `str` | Loads project-specific authority config |

---

## Outputs

`list[RetrievedChunk]` — same chunks, re-ordered by combined authority + similarity score.

---

## Scoring Formula

```
final_score = (1 - authority_weight) * similarity_score + authority_weight * authority_score

authority_score = (max_level - chunk.authority_level) / (max_level - 1)
# Level 1 → authority_score = 1.0
# Level 5 → authority_score = 0.0

authority_weight = 0.3  # configurable; 30% authority, 70% semantic similarity
```

This means a level-1 ECO chunk with 0.75 similarity beats a level-4 WhatsApp chunk with 0.82 similarity.

---

## Configuration

`authority_weight` should be configurable per project. A project with many informal WhatsApp decisions may want to lower the authority weight; a safety-critical project may want to raise it to 0.5+.

---

## Related

- [conflict-resolver.md](./conflict-resolver.md)
- [../../decisions.md → D07](../../decisions.md)
