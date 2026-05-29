---
id: response-builder
type: spec
status: not-implemented
phase: 1
last_updated: 2026-05-29
related:
  - ./query-engine.md
  - ../context-store/conflict-resolver.md
  - ../../decisions.md
  - ../../todo.md
---

# Module: Response Builder

> `backend/query/response_builder.py`

---

## Purpose

Take retrieved chunks and build a final response: LLM-generated answer grounded in retrieved context, plus structured source citations. Surfaces conflict labels (TRUSTED / SUPERSEDED) in Phase 2.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `query_text` | `str` | Original user question |
| `chunks` | `list[RetrievedChunk]` | From query engine (Phase 1) or conflict resolver (Phase 2+) |
| `role` | `str` | User role — affects answer framing in Phase 3 |

---

## Outputs

```python
@dataclass
class Response:
    answer: str                     # LLM-generated answer
    sources: list[Source]           # Cited chunks
    has_conflict: bool              # True if any TRUSTED/SUPERSEDED labels present
    confidence: float               # Avg cosine similarity of top-k chunks (0.0–1.0)

@dataclass
class Source:
    content: str                    # Chunk text excerpt
    source_file: str
    source_type: str
    timestamp: str
    authority_level: int
    label: str | None               # "TRUSTED" | "SUPERSEDED" | None (Phase 2+)
    instrument_tags: list[str]      # If applicable
    similarity_score: float
```

---

## Prompt Template (Phase 1)

```
You are NEXUS, an engineering project assistant. Answer the question using ONLY the provided context.
If the context does not contain enough information to answer, say so clearly.
Do not invent information not present in the context.

Context:
{formatted_chunks}

Question: {query_text}

Answer:
```

`formatted_chunks` format:
```
[Source 1 — {source_type} — {source_file} — {timestamp}]
{chunk.content}

[Source 2 — ...]
...
```

---

## Confidence Signal

```python
confidence = mean([chunk.similarity_score for chunk in top_k_chunks])
```

Display thresholds:
- `>= 0.80` → High confidence
- `0.60–0.79` → Medium confidence
- `< 0.60` → Low confidence — answer may be incomplete

This is stated explicitly in the UI, not hidden. See critique: [../../critique/technical.md](../../critique/technical.md).

---

## Phase 2 Addition — Conflict Labels

When conflict resolver returns `TRUSTED`/`SUPERSEDED` labels, the response builder:
1. Answers using the TRUSTED source as primary context
2. Includes both sources in the `sources` list with labels
3. Sets `has_conflict: True`
4. Adds a note in the answer: *"Note: a conflicting source was found. See sources panel."*

---

## LLM Configuration

- Model: Qwen2.5-7B via Ollama (configurable via `.env`)
- Endpoint: `http://ollama:11434/api/generate`
- Temperature: 0.1 (low; factual answers, not creative)
- Max tokens: 1024

---

## Related

- [query-engine.md](./query-engine.md)
- [../context-store/conflict-resolver.md](../context-store/conflict-resolver.md)
- [../../critique/technical.md](../../critique/technical.md)
