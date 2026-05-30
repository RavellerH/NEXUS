---
id: vector-databases
type: research
status: active
last_updated: 2026-05-30
tags: [vector-database, qdrant, pinecone, weaviate, milvus, pgvector, chromadb]
related:
  - ./INDEX.md
  - ./retrieval.md
  - ./embeddings.md
  - ./combinations.md
---

# Vector Databases

> **TL;DR**: Qdrant for self-hosted production. Pinecone for fastest time-to-market (managed). Weaviate for native hybrid search managed. pgvector for Postgres shops under 50M vectors. ChromaDB for development only.

---

## Performance Benchmarks (2025)

Tested at 100M vectors, HNSW ef_construction=128, m=16:

| Database | Version | Notes on QPS | p95 latency | Best at |
|----------|---------|-------------|------------|---------|
| **Qdrant** | 1.10.0 | ~41 QPS (high-recall strict mode) | ~20ms | Filtered search, self-host, Rust |
| **Pinecone** | Serverless | ~10,000 QPS | ~50ms (managed) | Operational simplicity, prototyping |
| **Weaviate** | 1.26.0 | ~5,000 QPS | ~30ms | Built-in hybrid search, managed cloud |
| **Milvus** | 2.4.3 | Best at billion-scale | Low at scale | Billion-vector scale, sharding |
| **pgvector** | 0.7.0 | 471 QPS (with pgvectorscale) | 5–8ms | Postgres teams, &lt;50M vectors |
| **ChromaDB** | 0.5+ | Low (not designed for scale) | — | Local dev, prototyping only |

**Important context**: QPS numbers vary by hardware, vector dimensionality, filter selectivity, and recall target. Qdrant's 41 QPS above is in strict high-recall mode (ef_search high). With 90% recall target, Qdrant achieves substantially higher QPS. Milvus/Zilliz Cloud leads on separate low-latency benchmarks.

---

## Hosting Model Comparison

| | Pinecone | Qdrant | Weaviate | Milvus | pgvector |
|--|---------|--------|---------|--------|---------|
| Managed cloud | ✅ Yes | ✅ Qdrant Cloud | ✅ Weaviate Cloud | ✅ Zilliz Cloud | ❌ (requires Postgres) |
| Self-hosted | ❌ No | ✅ Recommended | ✅ Yes | ✅ Yes | ✅ Yes |
| Migration complexity | High (proprietary) | Low | Medium | Medium | Low (standard SQL) |
| Hybrid search | Via metadata | ✅ Native | ✅ Native | ✅ Yes | pgvector + pg_trgm |
| Scalar filtering | ✅ Yes | ✅ Best-in-class | ✅ Good | ✅ Good | ✅ SQL |
| Sparse vector support | Limited | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No native |

---

## Database Profiles

### Qdrant
- Written in Rust → memory-efficient, low latency
- Best-in-class filtered vector search (filter by metadata while maintaining recall)
- Native support for dense, sparse, and multi-vector (ColBERT)
- Strong self-hosted story: Docker Compose single-file deployment
- Active open-source development
- **Rule of thumb**: Best choice for self-hosted production when you need filtering on metadata (e.g., project_id, document_type, date_range)

### Pinecone
- Fully managed, serverless
- Near-zero ops overhead; fastest path from prototype to production
- Proprietary API — migration to another DB requires re-ingestion
- High QPS at scale in managed mode
- **Rule of thumb**: Use for speed-to-market. Migrate when monthly cost exceeds $500–1,000 or vector count exceeds 50M

### Weaviate
- Built-in BM25 + dense hybrid search (no external BM25 index needed)
- GraphQL API; multi-tenancy (important for SaaS products)
- Weaviate Cloud Services for managed; self-hosted also supported
- Module system: plug-in vectorizers (OpenAI, Cohere, Ollama, local models)
- **Rule of thumb**: Best managed option when built-in hybrid search matters

### Milvus / Zilliz
- Purpose-built for billion-scale deployments
- Distributed architecture with sharding and replication
- Higher ops complexity than Qdrant
- Zilliz Cloud for managed version
- **Rule of thumb**: Start here only if you know you'll exceed 500M vectors

### pgvector
- PostgreSQL extension — no new infrastructure if you already run Postgres
- `pgvectorscale` (Timescale): adds 28× QPS improvement over base pgvector, closes gap with purpose-built DBs for &lt;100M vectors
- Full SQL filtering — joins, subqueries, transactions
- IVFFLAT or HNSW index types
- **Rule of thumb**: Ideal for Postgres shops, smaller corpora (&lt;50M vectors), teams wanting one fewer service

### ChromaDB
- Simple Python-native API; perfect for prototyping and local development
- Not designed for production scale or concurrent access
- No native hybrid search, no production-grade filtering
- **Rule of thumb**: Dev/test only. Graduate to Qdrant or pgvector before first client

---

## Scale Decision Guide

```
How many vectors at steady state?
├── <1M     → ChromaDB (dev) or pgvector (prod)
├── 1M–50M  → pgvector (if Postgres shop) or Qdrant
├── 50M–500M→ Qdrant or Weaviate
└── >500M   → Milvus / Zilliz Cloud
```

## Cost Decision Guide

```
What is your priority?
├── Fastest to production → Pinecone Serverless
├── Self-hosted, lowest ops → Qdrant (Docker Compose)
├── Native hybrid, managed → Weaviate Cloud
├── Postgres-native, simple → pgvector
└── Billion-scale → Milvus / Zilliz
```

---

## Migration Strategy

If you need to migrate vector databases later:

1. **Re-embedding is always required** unless the source DB exports raw vectors (some do, some don't)
2. **Metadata is portable** (JSON) — easier than vectors
3. **Index configuration must be recreated** (HNSW parameters, metric type)
4. **Avoid proprietary APIs as the only interface** — wrap in a thin abstraction layer (e.g., LlamaIndex VectorStore interface) to reduce migration cost

---

## Related

- [[embeddings|Embedding Models]] — the models that produce the vectors stored here
- [[retrieval|Retrieval Methods]] — HNSW and IVF index types are database-internal implementations of ANN search
- [[graph-rag|Graph RAG]] — Neo4j, Kuzu for graph storage; vector DBs for the hybrid side
- [[combinations|Best Stack by Use Case]] — database recommendations per use case
