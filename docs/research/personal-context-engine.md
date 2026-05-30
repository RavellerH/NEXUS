---
id: personal-context-engine
type: research
status: active
last_updated: 2026-05-30
tags: [personal-ai, context-engine, memory, identity, pkb, rewind, memgpt, second-brain]
related:
  - ./INDEX.md
  - ./personal-knowledge-base.md
  - ./karpathy-llm-os.md
  - ./memory.md
  - ./retrieval.md
  - ./combinations.md
  - ./overview.md
  - ./graph-rag.md
---

# Personal Context Engine

> **TL;DR**: A personal context engine is an AI system that knows who you are and builds on that knowledge over time. It differs from a common LLM not in reasoning capability but in *what it knows about you*. A common LLM is an expert stranger. A personal context engine is an expert who has been your colleague for years. The gap between those two is not marginal — it is the difference between a tool and a cognitive partner.

---

## Context Engineering — The 2025 Framing

In 2025, Gartner declared: *"context engineering is in, prompt engineering is out."*

**Context engineering** is formally defined as: *"the discipline of designing dynamic systems that provide the right information and tools, in the right format, at the right time, to give an LLM everything it needs to accomplish a task."*

The distinction:
- **Prompt engineering**: *How* to ask a question — one-time textual instructions
- **Context engineering**: *What information architecture* surrounds the ongoing interaction — dynamic, persistent, multi-source

A personal context engine is applied context engineering for an individual. The goal: at query time, automatically assemble the right personal context so the model has everything it needs without the user having to explain it.

---

## What "Personal Context" Actually Means

Before defining the system, define the concept.

**Context** in AI means: everything the model can see and reason over in a single inference call. Personal context adds a qualifier: this is context that is specific to one person — their history, decisions, preferences, vocabulary, relationships, and goals.

Personal context has five dimensions:

| Dimension | What it captures | Example |
|-----------|----------------|---------|
| **Episodic** | Past events and conversations | "In January I decided to use ChromaDB. Here's why." |
| **Semantic** | Facts about your world, people, projects | "AT-201 is the temperature transmitter on Unit 3." |
| **Preference** | How you like to work, communicate, decide | "Farhan prefers concise answers with examples, not theory." |
| **Temporal** | Time-ordered state of decisions and projects | "This project was on hold in March. It resumed April 15." |
| **Relational** | Your relationships and their context | "Ahmad is the site engineer on Project Tanjung." |

A system that captures and retrieves all five dimensions has personal context. Most current tools capture at best one or two.

---

## What a Common LLM Cannot Do

Claude, ChatGPT, and Gemini are trained on the world's text. They are extremely capable. They are also completely stateless with respect to you. At the start of every new conversation, they know nothing about:

- What you were working on yesterday
- What decisions you've made and why
- Your specific vocabulary ("AT-201", "NEXUS", "Phase 1")
- Who you work with and what their roles are
- How you like to be answered
- What you've already tried and ruled out
- What you've been thinking about for the past six months

**The expert stranger problem**: Asking a common LLM a question is like calling a senior consultant you've never met. They are brilliant and knowledgeable about the general domain. But they don't know your specific situation, your past decisions, or your constraints. You spend the first half of every call re-explaining context.

A personal context engine eliminates re-explanation. Every query starts with the system already knowing your context.

---

## What a Personal Context Engine Adds

### 1. Persistent Identity

The system maintains a model of who you are that persists between sessions:
- Your name and role
- Your active projects and their status
- Your preferences (communication style, answer format, level of detail)
- Your domain vocabulary (technical terms, project names, people's names)

When you start a new conversation, the system doesn't start blank — it starts with your profile loaded.

### 2. Episodic Memory

The system remembers past conversations and decisions:

```
You (6 months ago): "Let's use ChromaDB for now, with an eye toward Qdrant later."
You (today):        "Why did we choose ChromaDB?"
System:             "You chose ChromaDB in November 2025 because it was the simplest 
                    option for Phase 1. You noted you'd likely migrate to Qdrant when 
                    you need filtered search on metadata (date, doc type, revision)."
```

A common LLM cannot answer this question. A personal context engine can.

### 3. Semantic Memory (Personal Ontology)

The system builds and maintains a personal ontology — a model of the entities, concepts, and relationships in your world:

```
Entities:    [Project Tanjung, AT-201, Farhan Budiman, Ahmad (site eng), Phase 1]
Concepts:    [hybrid search, instrument tag precision, authority hierarchy]
Decisions:   [D01: self-hosted, D03: Qwen2.5-7B, ...]
Relationships: [Ahmad works on Tanjung, AT-201 is in Unit 3, D03 resolves the SEA gap]
```

When you ask a question, the system enriches your query with this ontology before retrieval. "What's the status of the transmitter issue?" becomes "What is the status of AT-201 on Project Tanjung?" — without you having to specify.

### 4. Temporal Reasoning

The system understands time-ordered context:

- What was true before vs. after a specific event
- Task continuity (you were in the middle of something last week)
- Decision history (what led to the current state)
- Stale knowledge detection (this decision was made before a major scope change)

Temporal reasoning is what separates a knowledge base query system from a personal context engine. "What did I think about X in Q1?" is unanswerable without temporal indexing.

### 5. Proactive Synthesis

The most powerful feature — the system surfaces connections you didn't ask for:

```
You: "What should I consider when designing the reranker for Phase 2?"

Common LLM:  [Generic answer about cross-encoders and latency]

Personal context engine:  
  "Based on your notes, you flagged two things relevant here:
   1. D14 (decision): BGE-v2-M3 was selected for multilingual SEA support
   2. Your note from March: 'AT-201 exact match is still failing under semantic
      reranking — the reranker is using dense signals only'
   So the key question for Phase 2 reranking is whether to use a cross-encoder 
   that's aware of your FTS5 exact match layer, or to rerank only semantic candidates."
```

Proactive synthesis is what makes the system feel like a colleague, not a search engine.

---

## The Personal Context Engine Architecture

### Overview

```
┌──────────────────── PERSONAL CONTEXT ENGINE ─────────────────────┐
│                                                                     │
│  INGESTION            INDEXING              RETRIEVAL              │
│  ──────────          ──────────            ──────────             │
│  Notes → parse    →  Atomic claims   →     Dense (semantic)       │
│  Decisions → tag  →  Entities        →     Sparse (exact)         │
│  Conversations   →  Relationships   →     Graph (entity links)    │
│  Voice → text    →  Temporal markers →    Temporal filter         │
│                                                                     │
│  CONTEXT ASSEMBLY                                                   │
│  ─────────────────                                                 │
│  Query → expand with personal ontology                             │
│  → retrieve from all stores                                        │
│  → assemble: [personal identity] + [retrieved context] + [query]  │
│  → LLM generates grounded response                                 │
│                                                                     │
│  MEMORY LAYER                                                       │
│  ─────────────                                                     │
│  Working: current conversation                                      │
│  Episodic: past conversations (Zep/Graphiti)                       │
│  Semantic: personal ontology (graph + vector)                      │
│  Procedural: how you work (learned from patterns)                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Context Assembly in Detail

Context assembly is the distinguishing engineering challenge of a personal context engine. For a given query, the system must decide:

```
What to include in the context window:

1. IDENTITY BLOCK (always included, ~200 tokens)
   User profile: name, role, active projects, key preferences
   
2. RETRIEVED KNOWLEDGE (~1,000–3,000 tokens)
   Most relevant chunks from personal KB, ranked by:
   - Semantic similarity to query
   - Recency (more recent = higher weight)
   - Relevance to current project context
   
3. EPISODIC CONTEXT (~500–1,000 tokens)
   Recent conversations on this topic
   Most relevant past decisions
   
4. TEMPORAL CONTEXT (~200 tokens)
   Current date context + active work state
   
5. QUERY (~100 tokens)
   User's actual question
   
Total: 2,000–4,500 tokens (fits in any modern context window)
```

The assembly budget forces prioritization. The system must score and rank personal context across all these dimensions before fitting it into the context window.

### The Personal Ontology Layer

The most underrated component. Building a model of your world:

```python
# Every note/decision/conversation updates the personal ontology
entities = {
    "AT-201": {"type": "instrument_tag", "project": "Tanjung", "unit": 3},
    "Ahmad": {"type": "person", "role": "site_engineer", "project": "Tanjung"},
    "Phase 1": {"type": "project_phase", "status": "in_progress", "start": "2026-06"},
}

relationships = [
    ("AT-201", "LOCATED_IN", "Unit 3"),
    ("Ahmad", "WORKS_ON", "Project Tanjung"),
    ("Phase 1", "USES_DECISION", "D03"),
]
```

When you say "the transmitter" without specifying which one, the system resolves it from the ontology based on current project context.

---

## Personal Context Engine vs. Existing Systems

### Current Tools and Their Limits

| System | What it does well | What it misses |
|--------|------------------|---------------|
| **ChatGPT / Claude** | World knowledge, reasoning | ~8K token memory cap. Stateless otherwise. Re-explain every session. |
| **NotebookLM** | Document-grounded Q&A (~13% hallucination vs ~40% for generic LLM) | Static uploads, no persistent identity, no episodic memory |
| **Rewind.ai / Limitless** | Records everything on your Mac; 14GB/month compressed; local-first | No semantic model. No synthesis. Cannot distinguish noise from signal. |
| **Mem.ai** | AI-organized notes, voice capture | Limited temporal reasoning. Cloud-only. No personal ontology. |
| **Notion AI** | AI within your workspace | No cross-source synthesis. No persistent personal model. |
| **MemGPT / Letta** (arXiv:2310.08560) | Two-tier memory + graph; 93.4% Deep Memory Retrieval accuracy | Complex to deploy. Framework, not personal context product. |
| **Mem0** (arXiv:2504.19413) | Hybrid vector+graph+KV; 90% token reduction; 26% better than OpenAI memory | Memory extracted from conversation; not proactively curated |
| **Zep + Graphiti** (arXiv:2501.13956) | Bi-temporal KG; 94.8% Deep Memory Retrieval; +18.5% LongMemEval | Enterprise-focused; requires significant infrastructure |

**The common failure mode**: These systems are either great at storage (no reasoning) or great at reasoning (no personal storage). A personal context engine requires both — and crucially, must connect them through the personal ontology.

### What Makes a True Personal Context Engine Different

1. **It builds a model of you, not just your notes.** The difference between "I have your documents" and "I understand your world" is the personal ontology.

2. **It reasons temporally.** Most systems return documents; a personal context engine tells you how your thinking has evolved.

3. **It synthesizes proactively.** When you start working on something, it surfaces what it knows is relevant without being asked.

4. **It improves with use.** Every interaction enriches the personal ontology, improves preference models, and fills in gaps in episodic memory.

5. **It runs on your data, under your control.** Cloud-dependent personal AI creates a trust and privacy problem. Self-hosted is the only viable model for sensitive professional or personal knowledge.

---

## The 10× Moments

These are the moments when a personal context engine feels obviously superior to a common LLM:

**1. The "why did we decide this?" query**
> "Why are we using ChromaDB instead of Qdrant?"
> System: *Retrieves D01 and your note from October: "Qdrant adds ops complexity; we're building first version with minimal infrastructure."*

**2. The "what did I miss?" synthesis**
> "I haven't looked at the reranking module in 2 months. What's changed?"
> System: *Surfaces decisions D14, two audit findings about multilingual reranking, and your open question from March.*

**3. The "tell me about this person" context load**
> "Ahmad is asking about the instrument tag issue again."
> System: *Loads Ahmad's context: site engineer on Tanjung, previous three conversations about AT-201, what was resolved and what's still open.*

**4. The "write in my style" task**
> "Draft an email to Ahmad about the delay on AT-201."
> System: *Knows your communication style from past emails, knows the AT-201 history, knows Ahmad's role — drafts something that sounds like you, not like a generic LLM.*

**5. The "what should I do next?" project query**
> "I'm picking up Phase 1 implementation today. What should I focus on?"
> System: *Knows current phase status, unresolved bugs (PRE-001/002/003), open questions (Q4, Q5), last work session context, and priority order from the audit.*

Each of these is unanswerable by a common LLM. Each is trivially answerable by a personal context engine with a good PKB.

---

## What NEXUS Is Building Toward

NEXUS's current architecture (EPC document search + Q&A) is a **project-scoped context engine** — it knows about a project, not about a person. The evolution toward a full personal context engine looks like:

```
Phase 1 (current): Project context engine
  → Knows: documents, specs, SOPs for one project
  → Can answer: "what does AT-201 data sheet say?"

Phase 2: Multi-project + team context
  → Knows: cross-project patterns, team decisions, role-specific context
  → Can answer: "how did we handle a similar tag issue on the last project?"

Phase 3 (personal layer): PM personal context engine
  → Knows: individual PM's decision history, preferences, communication style
  → Can answer: "given what I know about how you work, here's what I recommend"

Phase 4 (proactive): Chief of Staff AI
  → Knows: everything + tracks active work state
  → Can say: "you have three unresolved questions from last week that are now blocking Phase 2"
```

This is the product roadmap that Karpathy's LLM OS framing predicts as inevitable.

---

## Design Principles for Personal Context Engines

Based on research and the constraints of personal use:

1. **Capture must be frictionless.** If capturing is work, it won't happen. Voice → text, auto-import from other tools, passive capture where possible.

2. **The personal ontology is worth the investment.** Entity extraction and relationship mapping at ingestion time makes every future query dramatically better.

3. **Temporal indexing is non-negotiable.** Everything must have a timestamp. Queries like "what was I thinking in Q1?" are impossible without it.

4. **Privacy = self-hosted.** A system that knows everything about you cannot be cloud-dependent without serious trust risk.

5. **Proactive is better than reactive.** The highest-value behavior is surfacing relevant context without being asked. Design for this from the start — it requires temporal + project-state awareness.

6. **The answer must cite sources.** A personal context engine that hallucinates is worse than one that admits it doesn't know. Every answer should point to the exact note/document/decision it drew from.

7. **Graceful degradation.** If the PKB has a gap, the system should say so and offer to answer from general knowledge — not silently answer from weights and hallucinate.

---

## Related

- [[personal-knowledge-base|Personal Knowledge Base]] — the structured store the engine draws on
- [[karpathy-llm-os|Karpathy: LLM OS]] — the theoretical framing
- [[memory|Memory Systems]] — Mem0, Zep+Graphiti for the memory layer
- [[graph-rag|Graph RAG]] — Graphiti for temporal personal memory
- [[combinations|System Combinations]] — how all layers connect into a full stack
- [[overview|Context Engine Overview]] — context engine vs. RAG distinction
