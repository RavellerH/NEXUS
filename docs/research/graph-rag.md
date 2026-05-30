---
id: graph-rag
type: research
status: active
last_updated: 2026-05-30
tags: [graph-rag, knowledge-graph, microsoft, lightrag, neo4j, graphiti]
related:
  - ./INDEX.md
  - ./retrieval.md
  - ./memory.md
  - ./vector-databases.md
  - ./combinations.md
---

# Graph RAG

> **TL;DR**: GraphRAG wins on corpus-wide questions and multi-hop entity reasoning. Vector RAG wins on specific factual lookups and cost. Use graph when your questions span many documents, not just one.

---

## When Graph RAG Beats Vector RAG

| Scenario | Winner |
|----------|--------|
| "What are the main themes across these 10K documents?" | GraphRAG (global) |
| "What is the relationship between entity A and entity B?" | GraphRAG (local) |
| "What does section 4.2 of this contract say?" | Vector RAG |
| "Find documents similar to this one" | Vector RAG |
| Multi-hop reasoning across entities | GraphRAG |
| Low-cost first deployment | Vector RAG |
| Rapidly updated corpus | Vector RAG (graph re-indexing is expensive) |
| Legal/compliance — entity obligation mapping | GraphRAG |

---

## Microsoft GraphRAG

### Architecture

Two-stage LLM pipeline:

1. **Entity + relationship extraction**: LLM extracts entities and relationships from source documents, building a knowledge graph
2. **Community detection**: Leiden algorithm partitions the graph into hierarchical communities
3. **Community summarization**: LLM generates summaries at each community level

### Query Modes

| Mode | Best for | How it works |
|------|---------|--------------|
| **Global Search** | "What are the main themes?" | Aggregates community summaries hierarchically |
| **Local Search** | Entity-centric queries | Fans out from a seed entity through graph neighborhood |
| **DRIFT Search** | Hybrid | Local search augmented with community context |

### Performance

- Global sensemaking on 1M-token corpora: **+50–70% improvement** in answer comprehensiveness and diversity vs. vector RAG
- FinanceBench (ACL 2025): **6% reduction in hallucinations** and **80% reduction in token usage** vs. conventional RAG

### Serious Limitations

| Issue | Detail |
|-------|--------|
| **Indexing cost** | $33,000 to index 5GB of legal documents using GPT-4 class models |
| **Token waste** | For the same query: LightRAG used 100 tokens vs. GraphRAG's 610,000 in one case study |
| **Entity quality** | Extraction is noisy; entities require deduplication and cleaning |
| **No advantage for specific lookups** | Local Search vs. dense retrieval is a close race on factual queries |
| **Re-indexing** | Slow and expensive when corpus updates frequently |

**Verdict**: Use GraphRAG when you need global sensemaking on a relatively static corpus. The indexing cost must be amortized over many queries.

---

## LightRAG

Emerged in 2024 as a lower-cost alternative to Microsoft GraphRAG. Uses dual-level graph retrieval (local + global) at a fraction of the indexing cost.

| Comparison | Microsoft GraphRAG | LightRAG |
|------------|-------------------|---------|
| Indexing cost | Very high (GPT-4 calls per chunk) | Significantly lower |
| Query tokens | ~610,000 (case study) | ~100 (same case study) |
| Quality | High | Approaching comparable |
| Production readiness | Mature (Microsoft tooling) | Emerging |

**When to choose LightRAG**: GraphRAG's quality goals with a fraction of the budget. Best for teams where the $33K indexing cost is prohibitive.

---

## LlamaIndex Property Graph

Integrates knowledge graph construction directly into LlamaIndex. Supports multiple backends:

| Backend | Best for |
|---------|---------|
| NetworkX | Development, small corpora |
| Neo4j | Production, complex queries, large graphs |
| Kuzu | Embedded graphs, no external service |
| Memgraph | Real-time graph analytics |

Property graphs allow entity nodes to carry rich metadata (e.g., document type, source, timestamp), enabling **hybrid graph + vector queries**:

```python
# Example: find equipment → find related spec documents
graph_query = kg_index.as_query_engine(
    include_text=True,
    response_mode="tree_summarize"
)
result = graph_query.query("What components connect to pump P-101?")
```

More flexible and lower-cost than Microsoft GraphRAG. Less opinionated about community detection.

---

## Graphiti (Zep + Neo4j)

**Graphiti** introduces a **temporally-aware knowledge graph** for agent memory:

- Edges carry **timestamps and validity windows**: "fact was true from date A to date B"
- Supports **point-in-time queries**: "What did we know about this customer in Q1 2025?"
- Handles conflicting facts from different time periods correctly (newer fact supersedes older)

```
Entity: Customer Acme Corp
  ── [has_contract] ──> Contract #2024-001 (valid: 2024-01-01 → 2024-12-31)
  ── [has_contract] ──> Contract #2025-001 (valid: 2025-01-01 → present)
  ── [account_manager] ──> Sarah J. (valid: 2023-03-01 → 2025-02-15)
  ── [account_manager] ──> Michael K. (valid: 2025-02-16 → present)
```

Best suited for:
- CRM-style applications where context changes over time
- Compliance/audit trails ("what was the approved spec at time of installation?")
- Long-horizon agent memory where facts evolve

---

## Equipment Hierarchy Example (EPC Use Case)

GraphRAG is a strong fit for engineering knowledge with natural hierarchical structure:

```
Plant (Refinery Unit 2)
  └── Process Unit (Distillation Column T-201)
        └── Equipment (Heat Exchanger E-201)
              ├── Component (Shell side AT-201 transmitter)
              │     └── Datasheet (vendor: Yokogawa, model: EJA310A)
              └── Component (Tube side pressure relief PRV-201)
                    └── Datasheet (vendor: Emerson, set point: 15 barg)
```

A graph-native query: "What are all the instruments on the distillation unit and their calibration dates?" can traverse the hierarchy in a single hop; a vector RAG system would need to retrieve and join multiple separate chunks.

---

## Implementation Decision Guide

```
Do your queries span many documents or entities?
├── YES (themes, relationships, entity networks)
│   ├── Budget for high indexing cost?
│   │   ├── YES → Microsoft GraphRAG
│   │   └── NO → LightRAG
│   └── Need temporal/evolving facts?
│       └── YES → Graphiti (Zep)
└── NO (specific factual lookups, section content)
    └── Vector RAG + hybrid retrieval (much cheaper, faster)
```

---

## Related

- [[retrieval|Retrieval Methods]] — vector RAG is usually the comparison baseline
- [[memory|Memory Systems]] — Graphiti spans graph-RAG and agent memory
- [[combinations|Best Stack by Use Case]] — graph is recommended for legal, healthcare, EPC equipment hierarchies
- [[vector-databases|Vector Databases]] — Neo4j and Kuzu are graph backends; Qdrant/Weaviate handle the vector side
