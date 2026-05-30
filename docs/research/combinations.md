---
id: system-combinations
type: research
status: active
last_updated: 2026-05-30
tags: [combinations, use-cases, architecture, production, stack]
related:
  - ./INDEX.md
  - ./overview.md
  - ./retrieval.md
  - ./indexing.md
  - ./reranking.md
  - ./graph-rag.md
  - ./memory.md
  - ./embeddings.md
  - ./vector-databases.md
  - ./frameworks.md
  - ./evaluation.md
---

# Best System Combinations by Use Case

> **How to use this document**: Find your use case, read the recommended stack. Every recommendation comes from the evidence in the research files — not from vendor preference.

---

## Enterprise Knowledge Base

**Problem**: Large organization, many departments, thousands of documents, multiple users with different access levels.

| Layer | Recommendation | Alternative |
|-------|---------------|------------|
| **Indexing** | Hierarchical (parent-doc) + Contextual Retrieval | Semantic chunking |
| **Embedding** | text-embedding-3-large or voyage-3-large | BGE-M3 (self-hosted) |
| **Retrieval** | Hybrid (BM25 + dense) with metadata filtering | Dense + scalar filter |
| **Reranking** | BGE-v2-M3 (self-hosted) or Cohere Rerank 3.5 | MixedBread large-v2 |
| **Vector DB** | Qdrant (self-hosted) or Weaviate (managed hybrid) | pgvector |
| **Memory** | Mem0 for per-user personalization | None for first version |
| **Framework** | LlamaIndex for retrieval + LangGraph for agents | LlamaIndex only |
| **Access control** | Metadata-gated filtering at query time | Never post-retrieval |

**Key consideration**: Policy enforcement at retrieval time is non-negotiable. User A must not retrieve User B's documents.

---

## Customer Support / FAQ

**Problem**: Many users asking repetitive questions, per-user context matters, consistency is critical.

| Layer | Recommendation | Notes |
|-------|---------------|-------|
| **Indexing** | Fixed-size (256–512 tokens) + QA pair extraction as separate index entries | |
| **Embedding** | text-embedding-3-small (cheaper, sufficient) | |
| **Retrieval** | Hybrid — BM25 catches product codes and error strings exactly | |
| **Reranking** | MixedBread base-v2 (fast, lightweight) | |
| **Memory** | Mem0 or Zep for per-customer conversational context | |
| **Framework** | LangGraph for stateful multi-turn flows | |
| **Evaluation** | RAGAS faithfulness + answer relevancy in CI/CD pipeline | |

**Key concern**: Response consistency. Two users asking the same question should get equivalent answers.

---

## Code Search and Developer Assistant

**Problem**: Developers querying a codebase for functions, patterns, or documentation.

| Layer | Recommendation | Notes |
|-------|---------------|-------|
| **Indexing** | Function/class-level chunking (AST-aware, not token-count) | Tree-sitter |
| **Embedding** | Voyage code-3 (best recall) or CodeRankEmbed (open source) | |
| **Retrieval** | Hybrid — dense for semantic queries, BM25 for API names/identifiers | |
| **Reranking** | General cross-encoder fine-tuned on code if available | BGE-v2-M3 fallback |
| **Vector DB** | Qdrant or pgvector (easy to run alongside existing Postgres) | |
| **Memory** | Minimal — session-level conversation history | |
| **Framework** | LlamaIndex for ingestion; custom query layer for latency | |

**Key consideration**: Use AST-aware chunking (Tree-sitter) for clean function/class boundaries rather than line-count splitting.

---

## Legal / Contract Review

**Problem**: Lawyers querying across large document sets, exact citation accuracy is mandatory, access control by matter/client.

| Layer | Recommendation | Notes |
|-------|---------------|-------|
| **Indexing** | Clause-level semantic chunking + summary indexing for section nav | |
| **Embedding** | voyage-3-large or Cohere embed-v4 | Both strong on legal domain |
| **Retrieval** | Hybrid strongly — legal citation strings are exact-match sensitive | |
| **Reranking** | Cross-encoder (MixedBread large or Cohere Rerank 3.5) | |
| **Graph RAG** | ✅ Viable for cross-contract entity relationship queries | Deal rooms, M&A |
| **Vector DB** | Qdrant or Weaviate with row-level security | |
| **Memory** | Minimal for document review; Zep+Graphiti for ongoing client relationships | |
| **Evaluation** | Human review mandatory — automated RAGAS is insufficient | |

**Critical**: Row-level security by matter/client is non-negotiable. Document access must be isolated per engagement.

---

## Personal Knowledge Management (Obsidian-like)

**Problem**: Single user, notes corpus, want to query their own thinking and past research.

| Layer | Recommendation | Notes |
|-------|---------------|-------|
| **Indexing** | Note-level + atomic claim extraction (Zettelkasten-style) | |
| **Embedding** | text-embedding-3-small (cheaper, sufficient at this scale) | |
| **Retrieval** | Dense or hybrid — corpus is usually &lt;100K notes | |
| **Reranking** | Optional at this scale | |
| **Graph RAG** | ✅ High ROI — entity graph is cheap to build at &lt;10K notes | |
| **Vector DB** | pgvector or ChromaDB (small scale, local) | |
| **Memory** | Lightweight custom episodic store | Mem0 is overkill |
| **Framework** | Custom or LlamaIndex | LangGraph overhead unnecessary |

**Key insight**: Graph RAG is uniquely valuable here. Personal knowledge is inherently networked — Zettelkasten notes reference each other — and the graph makes these links queryable.

---

## Healthcare / Medical Records

**Problem**: Clinical queries, patient history, medical literature — multilingual (non-English), PHI/PII compliance mandatory.

| Layer | Recommendation | Notes |
|-------|---------------|-------|
| **Indexing** | Section-level per clinical document structure (SOAP, CCD/C-CDA) + UMLS/SNOMED concept extraction | |
| **Embedding** | Domain-specialized: BioMedBERT, ClinicalBERT, or fine-tuned voyage-3 | General models underperform |
| **Retrieval** | Hybrid — clinical guideline lookup (semantic) + entity code lookup (exact) | |
| **Graph RAG** | ✅ Multi-hop clinical reasoning (diabetes + nephropathy + ACE inhibitors) | |
| **Compliance** | PHI/PII filtering at indexing time; chunking must not straddle patient IDs | Mandatory |
| **Evaluation** | Automated metrics are insufficient — require clinical expert review loops | Life-safety critical |

**Critical**: Hallucination is life-safety-relevant. Source citation + clinical expert review loops are mandatory, not optional.

---

## EPC / Engineering Document Search

**Problem**: Mixed content — P&IDs, data sheets, specifications, revision-controlled drawings — multilingual teams in SEA.

| Layer | Recommendation | Notes |
|-------|---------------|-------|
| **Indexing** | Document-type-specific chunking per document type | See [[../modules/context-store/vector-store]] |
| **Embedding** | Cohere embed-v4 (multimodal: drawing thumbnails + text) or multilingual-e5-large (self-hosted) | |
| **Retrieval** | Hybrid with strong BM25 component — instrument tags are exact-match | AT-201 ≠ AT-202 |
| **Exact search** | SQLite FTS5 hybrid index for tags, part numbers, PO numbers | |
| **Reranking** | BGE-v2-M3 or Cohere Rerank | |
| **Graph RAG** | ✅ Equipment hierarchy graph (plant → unit → equipment → component) | |
| **Vector DB** | Qdrant or Weaviate (complex metadata filtering: tag/revision/date) | |
| **Revision control** | TTL-based invalidation; timestamp-filtered retrieval | Prefer current revision |

**This is NEXUS's primary domain.** See [[../decisions|NEXUS Decision Log]] for the specific choices made for the SEA EPC context.

---

## The Minimal Viable Stack (Any Domain)

If you're starting from zero:

```
1. Fixed-size chunking (512 tokens, 10% overlap)
2. Embedding: text-embedding-3-large (commercial) or BGE-M3 (self-hosted)
3. Vector store: pgvector or ChromaDB (dev), Qdrant (production)
4. Hybrid retrieval: BM25 + dense + RRF
5. Reranking: MixedBread base-v2
6. Framework: LlamaIndex

Upgrade path:
→ Add contextual retrieval (immediate quality boost)
→ Switch to hierarchical indexing (for multi-section documents)
→ Add Mem0 or Zep (for multi-turn agents)
→ Add GraphRAG (for entity relationships and global queries)
```

---

## Related

- [[overview|Overview]] — why these components are needed
- [[retrieval|Retrieval]] · [[indexing|Indexing]] · [[reranking|Reranking]] — individual component deep dives
- [[evaluation|Evaluation]] — how to measure if your chosen combination is working
