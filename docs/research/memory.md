---
id: memory-systems
type: research
status: active
last_updated: 2026-05-30
tags: [memory, agents, memgpt, letta, mem0, zep, episodic, semantic]
related:
  - ./INDEX.md
  - ./graph-rag.md
  - ./retrieval.md
  - ./frameworks.md
  - ./combinations.md
---

# Memory Systems

> **TL;DR**: By 2026 the dominant pattern is hybrid (vector + graph + short-term buffer). Pure vector memory is being replaced. Choose based on whether your facts evolve over time.

---

## Memory Taxonomy

| Type | What it stores | Retrieval mechanism | Scope |
|------|---------------|--------------------|----|
| **Working / In-context** | Current conversation, recent tool outputs | In-context, no retrieval | Current session |
| **Episodic** | Past conversation summaries, events with timestamps | Vector similarity + time filter | Cross-session |
| **Semantic** | Extracted facts, user preferences, entity properties | Vector + graph | Long-horizon |
| **Procedural** | Learned workflows, system prompts, tool use patterns | Key-value or prompt injection | Persistent |

Most production deployments need at least **working + episodic + semantic**. Procedural memory is less common and usually handled through system prompt engineering.

---

## MemGPT / Letta

**MemGPT** (2023) implemented a tiered memory model analogous to OS virtual memory:

```
┌─────────────────────────────────┐
│ Main Memory (in-context budget) │  ← Current conversation, recent facts
├─────────────────────────────────┤
│ External Storage (archival)     │  ← Long-term memory, past conversations
└─────────────────────────────────┘
       ↑ page-in / page-out ↓
```

The agent controls what moves between tiers via function calls. This enables effectively unlimited memory within a fixed context window budget.

**Letta** is the productized 2024–2025 successor:
- Open source (Apache 2.0)
- REST API for stateful agents
- Persistent agent state (memory survives restarts)
- Best suited for **long-running, document-heavy agent sessions** where context window overflow is the primary pain point

---

## Mem0

Multi-layer architecture combining three stores:

```
Incoming conversation/event
    ↓ LLM-based memory extraction
    ↓
┌──────────────┬──────────────┬──────────────┐
│ Vector Store │ Graph Store  │  KV Store    │
│ (semantic    │ (entity      │ (structured  │
│  similarity) │  relations)  │  facts)      │
└──────────────┴──────────────┴──────────────┘
    ↓ retrieval at query time
```

**Key differentiator**: **Active memory consolidation**. Mem0 merges and deduplicates memories over time rather than accumulating raw conversation history. When you learn the same fact in a new form, Mem0 updates the existing memory entry rather than adding a duplicate.

**Scale**: demonstrated scalable extraction and retrieval across millions of memory entries (Arxiv 2504.19413, 2025).

**Integrations**: LangChain, LlamaIndex, CrewAI, MultiOn.

**Graph backend support**: Neo4j and Kuzu.

---

## Zep + Graphiti

**Graphiti** is Zep's temporally-aware knowledge graph layer (Neo4j-backed):

- Each fact edge carries **validity timestamps**: `valid_from` → `valid_until`
- Handles conflicting facts from different time periods: newer supersedes older
- Enables **point-in-time queries**: "What was the customer's account status on March 15?"

```
User: "What was the approved pressure spec for AT-201 in 2024?"
→ Graphiti query: AT-201.pressure_spec WHERE valid_during(2024)
→ Returns: 15 barg (ECO-2024-003, superseded by ECO-2025-007 in 2025)
```

**Best suited for**:
- CRM / sales applications where context changes over time
- Compliance and audit trails
- EPC revision-controlled specifications
- Any domain where facts have a "version" or "validity period"

---

## LangMem

LangGraph-native memory layer from LangChain:
- First-class integration with LangGraph's state management
- Types: in-thread (short-term), cross-thread (long-term user facts), cross-agent (shared org memory)
- Suited for teams already using LangGraph for orchestration

---

## 2026 Comparison Matrix

| System | Memory types | Graph support | Temporal | Open source | Best for |
|--------|-------------|--------------|---------|-------------|---------|
| **Letta** | Working + semantic + episodic | No | No | ✅ Yes | Long-running agents with deep context |
| **Mem0** | Episodic + semantic + KV | ✅ Yes (Neo4j/Kuzu) | No | ✅ Yes | Multi-user apps, scalable fact memory |
| **Zep + Graphiti** | Episodic + semantic + temporal | ✅ Yes (Neo4j) | ✅ Yes | ✅ Yes | Time-evolving facts, CRM, compliance |
| **LangMem** | In-thread + cross-thread | No | No | ✅ Yes | LangGraph-native agents |
| **Custom vector store** | Semantic only | No | No | N/A | Simplest case, static facts |

---

## 2026 Dominant Production Pattern

**Hybrid: vector + graph + short-term episodic buffer**

Every serious production deployment layers at minimum:
1. **Short-term episodic buffer** — last N turns (in-context or compact summary)
2. **Semantic vector store** — long-horizon user/entity facts, similarity-based retrieval
3. **Entity relationship graph** — multi-entity reasoning, relationships, constraints

The pure vector store (Mem0 v1-era) is being replaced by this hybrid. The vector store handles "what facts about this entity exist?" while the graph handles "how are these entities related and what are the constraints between them?"

---

## Memory for Different Agent Types

| Agent type | Memory needs | Recommended |
|-----------|-------------|-------------|
| Chat assistant | Episodic (conversation history) | Letta or simple buffer |
| Personal assistant | Episodic + semantic (user preferences) | Mem0 |
| Customer-facing agent | Semantic + temporal (evolving customer context) | Zep + Graphiti |
| Research agent | Semantic (extracted facts from documents) | Mem0 or custom |
| Engineering co-pilot | Semantic + temporal (revision-controlled specs) | Zep + Graphiti |
| Multi-agent system | Cross-agent shared semantic | LangMem or Mem0 |

---

## Related

- [[graph-rag|Graph RAG]] — Graphiti and LlamaIndex Property Graph span memory and graph RAG
- [[retrieval|Retrieval Methods]] — episodic/semantic memory retrieval uses the same mechanisms as document retrieval
- [[frameworks|Frameworks]] — LangMem integrates with LangGraph; Mem0 integrates with LlamaIndex
- [[combinations|Best Stack by Use Case]] — memory recommendations per use case
