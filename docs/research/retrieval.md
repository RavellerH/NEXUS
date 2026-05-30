---
id: retrieval-methods
type: research
status: active
last_updated: 2026-05-30
tags: [retrieval, dense, sparse, hybrid, colbert, bm25]
related:
  - ./INDEX.md
  - ./overview.md
  - ./indexing.md
  - ./reranking.md
  - ./embeddings.md
  - ./vector-databases.md
---

# Retrieval Methods

> **TL;DR**: Start with hybrid (BM25 + dense + RRF). Add reranking. Use ColBERT when you need high recall and can afford 3–5× storage.

---

## The Four Families

| Method | Index type | Query time | Best for |
|--------|-----------|------------|---------|
| **Dense** (bi-encoder) | HNSW/IVF vector index | Fast (ANN) | Semantic similarity, natural language |
| **Sparse** (BM25/SPLADE) | Inverted index | Fast | Exact terms, entity names, codes, IDs |
| **Hybrid** (dense + sparse) | Both | Fast | Most production use cases |
| **Late interaction** (ColBERT) | Token-level vector index | Medium | High accuracy, domain shift, OOD |

---

## Dense Retrieval

### Bi-Encoders
Encode queries and documents **independently** into fixed-size vectors, then use approximate nearest-neighbor (ANN) search at query time. Documents are pre-encoded and indexed; only the query needs encoding at runtime.

- Fast at query time (ANN search in HNSW takes microseconds)
- Can be significantly improved with domain adaptation (fine-tuning on in-domain pairs)
- Single global vector compresses all meaning → some nuance is lost

### Cross-Encoders
Take query + document **together** in a single forward pass, producing a relevance score. Far more accurate than bi-encoders but cannot pre-index documents — used exclusively for **reranking** (see [[reranking]]), not first-stage retrieval.

---

## Sparse Retrieval

### BM25
The term-frequency/inverse-document-frequency retrieval function from 1994. Still a strong baseline and routinely competitive with dense retrieval:

- Outperforms `text-embedding-3-large` on most financial text metrics (Arxiv 2604.01733)
- Zero-shot: no in-domain training required
- Handles exact term matching perfectly: `AT-201`, `CBL-001-HV`, error codes, product SKUs, legal citation strings
- Fails on vocabulary mismatch: "myocardial infarction" ≠ "heart attack"

### SPLADE
Uses a transformer to produce **sparse vectors** where dimensions correspond to vocabulary terms with learned expansion weights. Bridges BM25's vocabulary mismatch gap — it can infer semantic relationships while maintaining sparsity for fast lookup.

Best for:
- Low-data-resource settings where fine-tuned dense models are unavailable
- When you want BM25-like speed + semantic generalization

---

## Hybrid Search (Dense + Sparse)

The dominant production pattern. Combine BM25/SPLADE scores with dense retrieval scores using **Reciprocal Rank Fusion (RRF)**:

```python
RRF_score(d) = sum(1 / (k + rank_r(d)) for r in retrieval_methods)
# k=60 is the standard constant
```

### Benchmark Numbers (MS MARCO, Recall@10)

| Method | Recall@10 |
|--------|-----------|
| BM25 alone | 11.9% |
| Dense alone | 13.9% |
| **Hybrid RRF** | **80.8%** |

A **580% relative improvement** over the best single-method. This is not a marginal gain.

### Two-Stage: Hybrid RRF → Cross-Encoder Reranking

| Metric | Score |
|--------|-------|
| Recall@5 | **0.816** |
| MRR@3 | **0.605** |

### Adaptive Weighting
Query-dependent alpha between dense and sparse (rather than fixed 50/50 blend) yields an additional **+2–7.5 percentage points** in Precision@1 and MRR@20 vs. static hybrids.

---

## Late Interaction: ColBERT

ColBERT produces a **matrix** of per-token vectors per document (rather than a single vector), then scores query–document pairs via MaxSim: for each query token, find the most similar document token, then sum.

```
score(q, d) = Σ_qi max_{dj} (qi · dj^T)
```

### ColBERTv2 + PLAID (2025 Production State)

| Improvement | Detail |
|-------------|--------|
| Index compression | Residual compression: 6–10× smaller vs. original ColBERT |
| Query latency | PLAID engine: up to **45× faster** on CPU, **7× on GPU** |
| Token pruning | 50–75% pruning: ≤2% effectiveness drop, 25–40% disk reduction, 30–50% latency drop |

### ColBERT Tradeoffs

| | ColBERT | Bi-encoder |
|--|---------|-----------|
| Accuracy | Higher (especially OOD) | Lower |
| Index size | 3–5× larger | Smaller |
| Latency | Medium | Fast |
| Domain shift | Handles well | Needs fine-tuning |
| Best for | High-accuracy production, domain shift | Standard retrieval |

---

## Multi-Vector Retrieval: BGE-M3

**BGE-M3** is a single model that simultaneously supports **dense, sparse, and multi-vector (ColBERT-style)** retrieval. This enables ensembling across all three modes within one index — a significant practical advantage.

- 100+ language support
- 568M parameters
- MTEB score: 63.0
- See [[embeddings]] for full model comparison

---

## Decision Guide

```
Is exact-match precision required?
├── YES (tag IDs, codes, names) → Hybrid (BM25 + dense) or SPLADE
└── NO (natural language, concepts)
    ├── In-domain data available for fine-tuning?
    │   ├── YES → Fine-tuned dense model + reranker
    │   └── NO → ColBERT (better OOD generalization) or BGE-M3
    └── Cost / latency sensitive?
        ├── YES → Bi-encoder ANN + cross-encoder reranker
        └── NO → ColBERT with PLAID
```

---

## Related

- [[embeddings|Embedding Models]] — which model to use for dense retrieval
- [[reranking|Reranking]] — second-stage precision improvement
- [[vector-databases|Vector Databases]] — what stores and serves the index
- [[indexing|Indexing Strategies]] — how documents are prepared for retrieval
