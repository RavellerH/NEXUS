---
id: context-engine-overview
type: research
status: active
last_updated: 2026-05-30
tags: [context-engine, rag, overview, fundamentals]
related:
  - ./INDEX.md
  - ./retrieval.md
  - ./indexing.md
  - ./memory.md
  - ./combinations.md
---

# What Is a Context Engine?

> A context engine is the structural layer that governs *everything the model sees at inference time*.
> RAG is a component of a context engine. It is not a context engine itself.

---

## Context Engine vs. Adjacent Systems

| System | Core job | What it lacks |
|--------|----------|---------------|
| **Search engine** | Returns ranked documents | No synthesis, no LLM, no memory |
| **Knowledge base** | Stores structured facts | No dynamic retrieval, no reasoning |
| **RAG pipeline** | Retrieves chunks → injects into LLM context | No governance, no memory, no policy layer |
| **Context engine** | Curates *everything* the model sees at inference time | — |

The canonical framing: **retrieval (RAG) is the transportation layer. Context engineering is the structural layer** that governs what actually ends up in the prompt.

---

## What a Context Engine Adds Over Plain RAG

### 1. Data Quality Gates
Filters ungoverned or stale chunks before they enter the prompt. A plain RAG pipeline retrieves whatever scores highest — a context engine decides whether that result is trustworthy enough to use.

### 2. Data Lineage
Traces every chunk back to its source, version, and owner. Required for citation, auditability, and debugging wrong answers.

### 3. Policy Enforcement
Applies row-level security, role-based access control, and redaction **at retrieval time** — not just at display time. A user without access to a document should not have that document's chunks returned by the retriever, regardless of what the UI shows.

### 4. Memory Integration
Maintains working, episodic, and semantic memory across turns and sessions. A plain RAG pipeline is stateless — every query starts from zero.

### 5. Context Assembly Logic
Decides *how* retrieved chunks are ranked, formatted, deduplicated, and combined with tool outputs, memory, and system instructions before the LLM sees them. The order, structure, and composition of the prompt directly affects answer quality.

### 6. Versioned Context Products
Manages retrieval units as managed artifacts with TTLs and changelogs. When a document is revised, old chunks are invalidated.

---

## The Five Problems Plain RAG Cannot Solve

| Problem | RAG limitation | Context engine solution |
|---------|---------------|------------------------|
| Confident but wrong answers | Any chunk that scores high gets retrieved | Quality gates + reranking + hallucination filters |
| Security violations | No access control at retrieval layer | Policy enforcement at query time |
| Stale answers | No TTL on indexed documents | Version tracking + TTL-based invalidation |
| Corpus-wide reasoning | "What are the main themes?" can't be answered by top-k chunks | GraphRAG global search |
| Per-session memory loss | Every query starts cold | Memory integration (episodic + semantic) |

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    LLM Generation Layer                  │
│     (Qwen2.5-7B, GPT-4o, Claude, Llama 3.3…)           │
├─────────────────────────────────────────────────────────┤
│                  Context Assembly Layer                  │
│   chunk ordering · deduplication · prompt formatting    │
│   memory injection · tool output integration            │
├──────────────┬──────────────────────┬───────────────────┤
│   Retrieval  │      Reranking       │      Memory       │
│   (hybrid)   │  (cross-encoder)     │  (episodic +      │
│              │                      │   semantic)       │
├──────────────┴──────────────────────┴───────────────────┤
│                     Index Layer                          │
│  vector store · FTS5/BM25 · knowledge graph · key-value │
├─────────────────────────────────────────────────────────┤
│                   Ingestion Layer                        │
│  chunking · embedding · metadata tagging · governance   │
├─────────────────────────────────────────────────────────┤
│                    Data Sources                          │
│  documents · databases · APIs · communication channels  │
└─────────────────────────────────────────────────────────┘
```

---

## When You Need Each Layer

| Scenario | Minimum viable stack | Full context engine |
|----------|---------------------|---------------------|
| Demo / prototype | Single vector store + LLM | — |
| Small team knowledge base | Hybrid retrieval + reranking | + Memory + lineage |
| Multi-user enterprise | + Access control + lineage | + Policy enforcement |
| Domain-specific (legal, medical, EPC) | + Domain embeddings + reranking | + Evaluation loop |
| Long-horizon agents | + Memory layer | + Full context assembly |
| Corpus-wide queries | + GraphRAG | + Hybrid with vector fallback |

---

## Related

- [[retrieval|Retrieval Methods]] — what "retrieval" means in practice
- [[indexing|Indexing Strategies]] — how documents become retrievable chunks
- [[memory|Memory Systems]] — how context persists across turns
- [[combinations|Best Stack by Use Case]] — practical guidance
