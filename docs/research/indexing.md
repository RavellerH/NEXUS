---
id: indexing-strategies
type: research
status: active
last_updated: 2026-05-30
tags: [indexing, chunking, contextual-retrieval, rag, embeddings]
related:
  - ./INDEX.md
  - ./retrieval.md
  - ./embeddings.md
  - ./reranking.md
  - ./overview.md
---

# Indexing Strategies

> **TL;DR**: Start with fixed-size (512 tokens, 10% overlap). Add contextual retrieval when you have the prompt caching budget. Use hierarchical for multi-section documents.

---

## Strategy Overview

| Strategy | Complexity | Recall lift | Indexing cost | Best for |
|----------|-----------|------------|---------------|---------|
| Fixed-size with overlap | Low | Baseline | Low | Prototyping, homogeneous docs |
| Semantic chunking | Medium | ~70% | Medium | Heterogeneous, topic-shift docs |
| Sentence-window | Medium | Medium | Medium | Precision-first with context hand-off |
| Late chunking | High | Good | High compute | Cross-referencing docs, pronouns |
| Contextual retrieval | High | **35–67%** failure rate reduction | High (LLM calls) | Production, high-stakes retrieval |
| Hierarchical indexing | Medium | Good | Medium | Long-form multi-section documents |
| Summary indexing | Medium | Good for global | Medium (LLM calls) | Corpus navigation, global queries |

---

## Fixed-Size Chunking with Overlap

The de facto default. Recommended starting point: **512 tokens with 10–20% overlap**.

```python
chunks = text_splitter.split(
    text=document,
    chunk_size=512,
    chunk_overlap=51  # ~10%
)
```

**When to use**: always start here and upgrade only when evaluation numbers justify it.

**Key decision**: chunk size. Smaller = more precise retrieval, less context. Larger = more context, more noise.

| Chunk size | Precision | Context quality | Use case |
|-----------|-----------|-----------------|---------|
| 128–256 tokens | High | Low | High-precision fact lookup |
| 512 tokens | Balanced | Balanced | General-purpose default |
| 1024–2048 tokens | Low | High | Summarization, topic analysis |

---

## Semantic Chunking

Uses embedding similarity to detect topic shifts: group sentences with similar embeddings, create a new chunk when cosine distance exceeds a threshold.

```python
# Topic boundary detected when cosine distance > threshold
if cosine_distance(embed(sentence_i), embed(sentence_i+1)) > 0.3:
    create_new_chunk()
```

**Benchmark**: up to **~70% lift** over naive fixed-size on some retrieval benchmarks.

**Cost**: slower and more expensive at indexing time. Best for heterogeneous documents where topic changes are abrupt.

---

## Sentence-Window Chunking

Indexes individual sentences but retrieves a **window of ±k surrounding sentences** for the LLM.

```
Index:    [s1] [s2] [s3] [s4] [s5]
Retrieved:         [s1 s2 s3 s4 s5]  ← window around s3 match
```

Balances retrieval precision (small index units) with generation quality (full context handed to LLM). Good for Q&A over dense factual documents.

---

## Late Chunking

Applies the full document through the encoder first (capturing cross-sentence context), **then pools token embeddings** into chunk-level vectors. Each chunk embedding "saw" the whole document, so pronouns and references resolve correctly.

Standard chunking vs. late chunking:
```
Standard: embed(chunk_text) in isolation
Late:     embed(full_document) → pool(token[chunk_start:chunk_end])
```

Good for documents with heavy cross-referencing. More compute-intensive at index time. Requires a model that supports long-context encoding (e.g., jina-embeddings-v3).

---

## Contextual Retrieval (Anthropic, September 2024)

The most impactful indexing innovation of 2024. For each chunk, an LLM generates a short context summary — "where this chunk sits in the document" — which is prepended before embedding.

```python
context_prompt = f"""
<document>{full_document}</document>
<chunk>{chunk_text}</chunk>

In 1-2 sentences, describe what this chunk is about within the context of the full document.
"""
context = llm.generate(context_prompt)
indexed_chunk = f"{context}\n\n{chunk_text}"
embed_and_index(indexed_chunk)
```

### Measured Results

| Approach | Top-20 retrieval failure rate |
|----------|------------------------------|
| Baseline | 5.7% |
| Contextual Embeddings | **3.7%** (−35%) |
| Contextual Embeddings + BM25 | **2.9%** (−49%) |
| Contextual Embeddings + BM25 + Reranking | **~1.9%** (−67%) |

### Cost Mitigation
LLM calls at indexing time are expensive. Anthropic mitigated this with prompt caching:
- Cache the full document text once
- Generate context for each chunk with a cache hit
- ~80–90% cost reduction vs. uncached generation

This makes contextual retrieval **viable for corpora of up to tens of millions of chunks**.

---

## Hierarchical Indexing (Parent Document Retriever)

Two-tier structure:
- **Small child chunks** (128–256 tokens) indexed for retrieval — high precision matches
- **Large parent sections** (1024–2048 tokens) passed to the LLM — high-quality context

```
Index:      [small chunk 1] [small chunk 2] [small chunk 3] ...
                        ↑           ↑
Retrieval result: matched!
                        ↓
LLM receives: [full parent section containing both chunks]
```

Addresses the precision vs. context tradeoff directly. Recommended for long multi-section documents (SOPs, technical manuals, contracts).

---

## Summary Indexing

Generates an LLM summary of each document or section and indexes the summary separately from the full text. Useful for:
- Global corpus queries ("What are the key themes?")
- Table-of-contents-style navigation
- Multi-hop reasoning where the first hop is "find the right document"

Often combined with hierarchical indexing: summary index for navigation, child chunks for factual retrieval.

---

## Chunking by Document Type

A critical design decision often overlooked. Naive fixed-size chunking applied uniformly produces poor results for structured documents.

| Document type | Problem with naive chunking | Recommended strategy |
|--------------|---------------------------|---------------------|
| Legal contracts | Breaks clause boundaries | Clause-level semantic chunking |
| Excel BOM | Severs row from column headers | Row-level, headers prepended |
| DOCX SOP | Splits numbered steps mid-instruction | Section heading + step preservation |
| P&ID drawings | Tag IDs disconnected from specs | Tag-region-aware chunking |
| WhatsApp chats | Cuts conversation threads | Message-level, date-window grouping |
| Email threads | Severs reply context | Message-level, thread-aware |
| Code files | Mid-function splits | Function/class-level (AST-aware) |

See [[../modules/context-store/vector-store|NEXUS Vector Store]] for EPC-specific chunking decisions.

---

## Decision Flowchart

```
What is your document type?
├── Structured (contracts, SOPs, BOMs)
│   └── Use document-type-specific chunking → Hierarchical with summary
├── Unstructured long-form (research, reports)
│   ├── Budget for LLM calls?
│   │   ├── YES → Contextual Retrieval + Hierarchical
│   │   └── NO → Semantic Chunking + Sentence-window
│   └── Cross-referencing heavy?
│       └── YES → Late chunking
└── Short-form (chat messages, Q&A pairs, news)
    └── Fixed-size (128–256 tokens) or sentence-level
```

---

## Related

- [[retrieval|Retrieval Methods]] — how indexed chunks are found at query time
- [[embeddings|Embedding Models]] — what encodes the chunks
- [[reranking|Reranking]] — post-retrieval precision improvement
- [[frameworks|Frameworks]] — LlamaIndex has built-in support for most strategies above
