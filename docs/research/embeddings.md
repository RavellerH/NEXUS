---
id: embedding-models
type: research
status: active
last_updated: 2026-05-30
tags: [embeddings, mteb, multilingual, bge-m3, voyage, openai, cohere]
related:
  - ./INDEX.md
  - ./retrieval.md
  - ./indexing.md
  - ./vector-databases.md
---

# Embedding Models

> **TL;DR**: For self-hosted general use: BGE-M3. For multilingual production: Qwen3-Embedding-8B or BGE-M3. For commercial managed: Cohere embed-v4 (also multimodal) or Voyage voyage-3-large. Always run in-domain evaluation before committing.

---

## Benchmark Context

**MTEB** (Massive Text Embedding Benchmark) measures performance across retrieval, clustering, classification, reranking, and more.

**Important**: MTEB v2 (2026) is not directly comparable to MTEB v1 scores. The numbers below use MTEB v1 unless noted. A model that leads overall may underperform on your specific domain.

---

## Commercial / Closed Models

| Model | MTEB avg | Dims | Key strengths |
|-------|---------|------|--------------|
| **OpenAI text-embedding-3-large** | 64.6 | 3072 (matryoshka, reducible to 256) | General purpose, widely integrated, reliable |
| **Cohere embed-v4** | 65.2 | 1024 | Strong multilingual, **natively multimodal** (image+text), good hybrid retrieval |
| **Voyage voyage-3-large** | ~65–66 (retrieval MTEB) | 1024 | Best-in-class retrieval-focused, leads on BEIR domains |
| **Voyage code-3** | — | 1536 | Code-optimized: **+4–8 Recall@10** over text-embedding-3-large on code corpora |

---

## Open-Source / Open-Weight Models

| Model | MTEB avg | Dims | Params | Key strengths |
|-------|---------|------|--------|--------------|
| **BGE-M3** (BAAI) | 63.0 | 1024 | 568M | Tri-mode (dense+sparse+multi-vector), 100+ languages |
| **NV-Embed-v2** (NVIDIA) | 72.31 | 4096 | ~7B | Highest open MTEB v1 overall; LLM-based |
| **GTE-Qwen2-7B-Instruct** | ~72 | 3584 | 7B | Strong multilingual, instruction-tuned |
| **Qwen3-Embedding-8B** (Alibaba) | 70.58 (multilingual MTEB) | 4096 | 8B | **2025 MTEB multilingual leaderboard leader** |
| **Microsoft Harrier-OSS-v1** | **74.3** (MTEB v2) | — | 27B | 2026 open-weight MTEB v2 leader |
| **multilingual-e5-large-instruct** | ~62 | 1024 | 560M | Reliable, widely deployed multilingual baseline |

---

## Multilingual Leaders

For SEA languages (Bahasa Indonesia, Malay, Filipino, Thai) and cross-lingual retrieval:

| Model | Coverage | Notes |
|-------|---------|-------|
| **BGE-M3** | 100+ languages | Tri-mode; dense+sparse+ColBERT in one model |
| **Qwen3-Embedding-8B** | Strong CJK + SEA | MTEB multilingual leader 2025 |
| **multilingual-e5-large** | 100+ languages | The reliable workhorse; widely deployed |
| **Cohere embed-v4** | 100+ languages | Commercial; also multimodal |

**Important caveat**: Cross-lingual retrieval (query in Bahasa, documents in English) is significantly worse than monolingual. Use monolingual retrieval when possible, and choose a model explicitly trained on your target languages.

---

## Code Embeddings

| Model | Strengths | Notes |
|-------|---------|-------|
| **Voyage code-3** | Best retrieval on code corpora | +4–8 Recall@10 vs. text-embedding-3-large |
| **CodeRankEmbed** | Purpose-built; CodeSearchNet | Open source; competitive performance |
| **BGE-M3** | Reasonable fallback | Not code-specialized; handles polyglot repos |

For code repositories mixing natural language comments, docstrings, and code tokens, BGE-M3 is a reasonable open-source choice. For pure code retrieval performance, use a code-specialized model.

---

## Multimodal Embeddings

| Model | Input types | Notes |
|-------|------------|-------|
| **Cohere embed-v4** | Text + images | Natively multimodal; OCR-free document retrieval |
| **GPT-4o embeddings** | Text + images | Early support; maturing |
| **CLIP / SigLIP variants** | Image + text | Not suited for long-form document contexts |

For systems that need to retrieve both text and images in a unified space (e.g., engineering drawings + specifications), Cohere embed-v4 is currently the strongest commercial option.

---

## Matryoshka Embeddings

OpenAI's `text-embedding-3-large` and some other models support **matryoshka representation learning**: the embedding can be truncated to lower dimensions while retaining most of its information.

```python
# Full 3072-dim embedding
embedding = embed("text", dimensions=3072)

# Truncated 256-dim embedding (much cheaper to store/query)
embedding_small = embed("text", dimensions=256)
```

This allows storage/cost/quality tradeoffs:
- 256d: good for high-throughput, storage-limited applications
- 1536d: balanced
- 3072d: maximum quality

---

## Choosing an Embedding Model

```
Do you need self-hosted (data never leaves your infra)?
├── YES
│   ├── Multilingual required?
│   │   ├── YES → BGE-M3 (560M, tri-mode) or Qwen3-Embedding-8B (8B, best multilingual)
│   │   └── NO  → multilingual-e5-large (reliable, small) or NV-Embed-v2 (best quality, 7B)
│   └── Code-heavy corpus?
│           └── CodeRankEmbed or BGE-M3
└── NO (commercial API acceptable)
    ├── Multimodal needed (images + text)?
    │   └── Cohere embed-v4
    ├── Best retrieval quality?
    │   └── Voyage voyage-3-large
    └── General purpose, widely integrated?
        └── OpenAI text-embedding-3-large
```

---

## Storage Considerations

| Dim | Float32 per vector | 1M vectors |
|-----|-------------------|------------|
| 256 | 1 KB | ~1 GB |
| 768 | 3 KB | ~3 GB |
| 1024 | 4 KB | ~4 GB |
| 3072 | 12 KB | ~12 GB |
| 4096 | 16 KB | ~16 GB |

At 1024 dimensions (BGE-M3, multilingual-e5-large, Cohere embed-v4), storage is manageable on most hardware. At 4096d (NV-Embed-v2, Qwen3-Embedding-8B), plan for quantization or dimension reduction.

---

## Related

- [[retrieval|Retrieval Methods]] — BGE-M3 supports dense, sparse, and multi-vector retrieval
- [[vector-databases|Vector Databases]] — stores the computed embeddings
- [[indexing|Indexing Strategies]] — embedding model choice affects chunking decisions (dimension lock-in)
- [[../modules/context-store/vector-store|NEXUS Vector Store]] — uses `multilingual-e5-large` (1024d) for SEA multilingual support
