---
id: reranking
type: research
status: active
last_updated: 2026-05-30
tags: [reranking, cross-encoder, rag, retrieval, cohere, bge]
related:
  - ./INDEX.md
  - ./retrieval.md
  - ./embeddings.md
  - ./frameworks.md
---

# Reranking

> **TL;DR**: Reranking is the **single highest-ROI addition** to a basic RAG pipeline. Retrieve 20–100 candidates; rerank to top 3–10 for the LLM.

---

## Why Reranking Works

First-stage retrieval (bi-encoder ANN) optimizes for speed — it retrieves *candidates*. The retriever's representation of a query and document are computed independently, so nuanced relevance is lost. A cross-encoder reranker scores each candidate *with full query–document interaction*, producing a far more accurate relevance score — but only for a small candidate set, not the entire corpus.

```
Full corpus
    ↓ First-stage retrieval (fast, recall-focused)
Top-k candidates (k=20–100)
    ↓ Cross-encoder reranking (accurate, precision-focused)
Top-n results (n=3–10)
    ↓ LLM generation
```

---

## Cross-Encoder Reranker Comparison (2025–2026)

| Model | BEIR NDCG@10 | ELO (Agentset) | Self-hosted? | Notes |
|-------|-------------|----------------|--------------|-------|
| **Zerank 2** | — | **1638** | ✅ | Agentset leaderboard leader, 2026 |
| **Cohere Rerank v4.0 Pro** | — | **1629** | ❌ API only | Strong on semi-structured JSON, multi-page docs |
| **MixedBread mxbai-rerank-large-v2** | **57.49** | — | ✅ | Open-weight, commercially permissive, leads BEIR |
| **MixedBread mxbai-rerank-base-v2** | 55.57 | — | ✅ | Smaller, faster, strong baseline |
| **BGE Reranker v2-M3** | Competitive | — | ✅ | Open-source reference; multilingual via M3 |
| **Pinecone Rerank V0** | Leads on 6/12 BEIR datasets | — | ❌ API only | Best average across a 12-dataset evaluation |
| **Cohere Rerank 3** | — | — | ❌ API only | Previous generation; still widely deployed |

### Selection Guide

| Need | Recommendation |
|------|---------------|
| Self-hosted, best quality | MixedBread large-v2 or Zerank 2 |
| Multilingual reranking | BGE Reranker v2-M3 |
| Managed, simplest ops | Cohere Rerank 3.5 or Pinecone Rerank |
| Budget-constrained, self-hosted | MixedBread base-v2 or BGE-reranker-base |

---

## LLM-as-Reranker

### RankGPT

Uses a generative LLM to rerank via **instructional permutation generation**: the LLM is given the query and a list of candidate passages, then asked to output a reordered permutation.

```
Given query: "What is AT-201's operating pressure?"
Rank these passages: [P1, P2, P3, P4, P5]
Output: [P3, P1, P5, P2, P4]
```

A **sliding window strategy** processes document lists in segments to handle large candidate sets within the context window limit.

**Advantages:**
- Strong reasoning about relevance nuances
- Supports multi-criteria ranking ("most recent and most authoritative")
- Can explain its ranking decisions

**Disadvantages:**
- High latency (full LLM forward pass per rerank request)
- High cost (LLM API charges per reranking call)
- Non-deterministic
- **Not suitable for synchronous low-latency pipelines**

**Best for**: async batch jobs, high-stakes retrieval pipelines where accuracy outweighs cost, cases where explainability is required.

### LLM Blender

Ensembles multiple LLM outputs via PairRanker (cross-encoder) and GenFuser. More suited to **answer fusion** than retrieval reranking.

---

## Reranking in Practice

### Recommended Configuration

```python
# First stage: retrieve more than you'll use
candidates = retriever.retrieve(query, top_k=20)

# Second stage: rerank to precision
reranked = reranker.rerank(query, candidates, top_n=5)

# Pass only the top-n to LLM
answer = llm.generate(query, context=reranked)
```

### k and n Values

| Use case | First-stage k | Reranked n |
|----------|-------------|-----------|
| Simple Q&A | 10–20 | 3–5 |
| Complex multi-hop | 30–50 | 5–10 |
| Safety-critical (legal, medical) | 50–100 | 10–20 |

### Cost vs. Quality Tradeoff

Adding reranking increases latency by ~50–200ms and adds API cost (Cohere) or compute (self-hosted). The retrieval quality improvement typically justifies this cost at the **k=20→n=5 level**. At k=5→n=3, the gain is marginal and may not justify the overhead.

---

## Reranking + Contextual Retrieval

From Anthropic's measurements, the combined effect of Contextual Retrieval + reranking delivers the best-known results on their benchmark:

| Configuration | Failure rate reduction |
|--------------|----------------------|
| Baseline RAG | 0% |
| + Contextual Embeddings | −35% |
| + Contextual Embeddings + BM25 | −49% |
| + Contextual Embeddings + BM25 + Reranking | **−67%** |

---

## Related

- [[retrieval|Retrieval Methods]] — first-stage retrieval produces the candidates that reranking scores
- [[embeddings|Embedding Models]] — BGE-M3 supports both embedding and reranking
- [[indexing|Indexing Strategies]] — contextual retrieval + reranking is the highest-performing combination
