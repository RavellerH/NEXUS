---
id: conflict-resolver
type: spec
status: not-implemented
phase: 2
last_updated: 2026-05-29
related:
  - ./vector-store.md
  - ./authority-ranker.md
  - ../query/response-builder.md
  - ../../decisions.md#d07
  - ../../todo.md
---

# Module: Conflict Resolver

> `backend/context_store/conflict_resolver.py`

---

## Purpose

Detect when two or more retrieved chunks make contradictory claims about the same topic. Label each chunk as `TRUSTED` (higher authority) or `SUPERSEDED` (lower authority or older version). Surface both in the response so the user sees the conflict, not a hidden resolution.

---

## Phase

Phase 2 — not required for MVP. Query engine works without it in Phase 1 (no conflict detection, just top-k results).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `chunks` | `list[RetrievedChunk]` | Top-k results from vector store query |
| `project_id` | `str` | For loading project-specific authority hierarchy |

---

## Outputs

```python
@dataclass
class ResolvedResult:
    chunks: list[RetrievedChunk]
    conflicts: list[Conflict]

@dataclass  
class Conflict:
    trusted_chunk: RetrievedChunk      # Higher authority
    superseded_chunk: RetrievedChunk   # Lower authority
    conflict_type: str                 # "authority" | "version" | "contradiction"
    explanation: str                   # Human-readable e.g. "ECO-2024-003 supersedes SOP-Rev-B"
```

---

## Conflict Detection Strategy

### Method 1: Authority + semantic similarity

If two chunks have cosine similarity > 0.85 (very similar topic) but different authority levels → flag as potential conflict. The higher-authority chunk wins.

### Method 2: Version detection

If two chunks from the same source file type have different version numbers or dates for the same document → flag the older one as `SUPERSEDED`.

### Method 3: Direct contradiction (Phase 2+)

Use the LLM to evaluate whether two high-similarity chunks actually contradict each other:
```
Given these two passages, do they make contradictory claims? 
Passage A: {chunk_a.content}
Passage B: {chunk_b.content}
Answer: yes/no + explanation
```
This is expensive (extra LLM call). Cache results. Only run when similarity > 0.9.

---

## Authority Hierarchy

Loaded from project config. Default per [decisions.md D07](../../decisions.md):

| Level | Source type | Notes |
|-------|------------|-------|
| 1 | Signed ECO | Overrides everything |
| 2 | Approved vendor datasheet | |
| 3 | Internal SOP (latest version) | |
| 4 | WhatsApp (from project lead) | Author-dependent |
| 5 | Drafts, old revisions | |

PM can reconfigure per project via admin panel (Phase 3).

---

## Related

- [authority-ranker.md](./authority-ranker.md)
- [vector-store.md](./vector-store.md)
- [../query/response-builder.md](../query/response-builder.md)
- [../../decisions.md → D07](../../decisions.md)
