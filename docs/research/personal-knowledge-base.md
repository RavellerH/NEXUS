---
id: personal-knowledge-base
type: research
status: active
last_updated: 2026-05-30
tags: [pkb, zettelkasten, para, obsidian, atomic-notes, personal, knowledge-management]
related:
  - ./INDEX.md
  - ./retrieval.md
  - ./indexing.md
  - ./memory.md
  - ./embeddings.md
  - ./graph-rag.md
  - ./personal-context-engine.md
  - ./karpathy-llm-os.md
---

# Personal Knowledge Base

> **TL;DR**: A personal knowledge base is the curated, linked store of your own thinking. The best design is atomic (one idea per note), linked (bidirectional references), and small (under 10K notes covers 95% of practitioners). The technical stack for personal scale is radically simpler than enterprise RAG — SQLite + a small embedding model is sufficient. The hard part is not the technology; it's the capture and linking discipline.

---

## Why Personal Scale Changes Everything

Enterprise knowledge management deals with thousands of contributors and millions of documents. A personal knowledge base is built by one person, for one person. This changes every technical decision:

| Dimension | Enterprise | Personal |
|-----------|-----------|---------|
| Corpus size | 100K–10M chunks | 1K–100K notes |
| Contributors | 100–10,000 users | 1 user |
| Query volume | 100–10,000/day | 1–50/day |
| Structure variance | High (many formats) | Low (one person's style) |
| Context needed | Document metadata | Your own history, preferences |
| Right tool | Qdrant + hybrid retrieval | SQLite + small embed model |
| Indexing cadence | Continuous pipeline | On note save / nightly |

The technical overhead of production RAG (distributed vector DBs, rerankers, chunking pipelines, auth) is unnecessary at personal scale. **The constraint is human capture discipline, not technology**.

---

## The Foundational Models

### Zettelkasten (Niklas Luhmann)

Luhmann developed this system in the 1950s–1980s, producing 70+ books and 400+ papers. Core principles:

1. **Atomic notes**: One idea per note. Not one document, not one topic — one _claim_ or _observation_.
2. **Permanent notes**: Written in your own words, as if explaining to a future reader who has no context.
3. **Linked notes**: Every note references at least one other note. The link is the unit of thinking, not the note.
4. **No hierarchy**: No folders, no categories. Only links and link clusters.
5. **Emergence**: The structure of your knowledge emerges from the links you make, not from a pre-imposed taxonomy.

**Digital implementations**: Obsidian, Logseq, Roam Research, Notion (partial), Foam (VS Code).

**Distinction — note types**:
- **Fleeting notes**: Quick captures (voice memos, scribbles). Ephemeral — processed within 48h or discarded.
- **Literature notes**: Summaries of what you read/heard. One note per source. In your own words.
- **Permanent notes**: The distilled insight, linked into the knowledge graph. Lives forever.

### PARA (Tiago Forte)

Projects–Areas–Resources–Archives. A folder-based system for organizing all digital information:

| Bucket | Definition | Example |
|--------|-----------|---------|
| **Projects** | Active work with a deadline | "NEXUS Phase 1 build" |
| **Areas** | Ongoing responsibility | "Engineering", "Health" |
| **Resources** | Reference material without a project | "Embeddings research" |
| **Archives** | Inactive items from above | "Old client proposals" |

PARA is output-oriented: everything is captured in the context of what you're currently working on.

**PARA vs Zettelkasten**: They are complementary, not competing. PARA organizes action-oriented material. Zettelkasten builds the permanent idea graph. Many practitioners use PARA for project notes and Zettelkasten for permanent insight.

### Progressive Summarization (Tiago Forte)

A layering technique for converting raw captures into retrievable knowledge:

```
Layer 0: Raw capture (paste, quote, voice transcript)
Layer 1: Bold key passages
Layer 2: Highlight the best of the bold
Layer 3: Executive summary in your own words
Layer 4: Remix into permanent note
```

Progressive summarization defeats the "saved but never read" trap. You only go deeper on notes you return to.

### Maps of Content (Nick Milo, Linking Your Thinking)

A MOC is a note that acts as a hub: it lists and links other notes on a theme without containing their content. MOCs:
- Surface clusters in the graph without imposing rigid hierarchy
- Serve as entry points for a domain
- Are themselves permanent notes that can be linked to

**Example**:
```markdown
# MOC: Context Engines

This note maps what I know about context engine design.

## Core concepts
- [[what-is-a-context-engine]]
- [[context-vs-rag-distinction]]

## Technical layers
- [[retrieval-methods-overview]]
- [[chunking-strategy-tradeoffs]]

## Personal application
- [[nexus-architecture-decisions]]
```

---

## Efficient PKB Design

### The Minimum Viable Structure

A PKB does not need to start with a perfect architecture. The minimal structure that produces value:

```
1. One note = one atomic claim (not a topic, not a document)
2. Every note links to at least one other note
3. One MOC per active project / area
4. Daily or weekly review to process fleeting notes into permanent ones
```

**Anti-patterns that kill PKBs**:
- Long notes (becomes a blog post, not a knowledge graph node)
- Over-tagging (taxonomy work substitutes for thinking work)
- Perfectly organizing instead of linking
- Waiting until you understand something fully before noting it
- Never revisiting notes (the purpose is synthesis, not storage)

### Size and Density

Research on personal PKBs in practice:

| Notes | User profile |
|-------|-------------|
| < 100 | Just starting; too sparse for emergence |
| 100–500 | Early graph; first "surprise" connections appear |
| 500–2,000 | Active practitioner; MOCs become essential |
| 2,000–10,000 | Experienced; the graph becomes a cognitive extension |
| 10,000+ | Power user; search and retrieval become bottlenecks |

**The 10K threshold**: Most practitioners do not exceed 10,000 notes. At this scale, a simple SQLite FTS + small embedding model retrieves with sub-100ms latency on commodity hardware.

### Note Granularity Tradeoff

| Chunk size | Retrieval | Synthesis | Maintenance |
|-----------|----------|----------|-------------|
| One word / tag | Poor | Poor | Low |
| One sentence | Poor | Good | High |
| One claim / insight | **Best** | **Best** | Medium |
| One document / article | Low | Poor | Low |

Atomic claim is the sweet spot. "Hybrid RRF outperforms dense-only by 580% on Recall@10" is a retrievable, linkable, shareable unit. "Retrieval" is not.

---

## Technical Stack for Personal Scale

### The Minimal Viable Stack

```
Storage:    SQLite (notes + FTS5 for keyword) + filesystem (markdown files)
Embeddings: nomic-embed-text (768d, local) or multilingual-e5-small (384d)
Vector:     SQLite-vec or ChromaDB (local, <10M vectors)
LLM:        Ollama (Qwen2.5-7b or llama3.2:3b for fast queries)
Interface:  Obsidian / custom web UI / CLI
```

**Why SQLite**: A 10,000-note PKB with 768-dim embeddings uses ~30MB of vector data. SQLite with the sqlite-vec extension handles this trivially. No Qdrant, no Weaviate, no Docker required.

**Why small embedding model**: Personal notes are short (50–200 words), stylistically consistent (your own writing), and semantically dense. A 384-dim model retrieves almost as well as 1024-dim for this use case while being 10× faster and 4× smaller.

### Personal Knowledge Graph

At <10K notes, a full knowledge graph is buildable and queryable:

```python
# Extract entities and relationships at note-write time
# At personal scale: run locally, no cost
for note in new_notes:
    entities = extract_entities(note)   # spaCy or local LLM
    links = parse_wikilinks(note)       # [[linked-note]] syntax
    claims = extract_claims(note)       # sentence-level atomic claims
    store_graph(entities, links, claims)
```

**Personal graph structure**:
- Nodes: notes, people, projects, concepts, decisions
- Edges: [[wikilinks]], entity co-occurrence, claim dependencies, temporal sequence
- Temporal layer: when was this known? what came before/after?

### Retrieval at Personal Scale

For a 10,000-note corpus, retrieval is fast by any method:

| Method | Latency (10K notes) | Notes |
|--------|--------------------|----|
| SQLite FTS5 | <5ms | Best for exact keywords, names, dates |
| Dense (ChromaDB local) | <20ms | Best for semantic/concept queries |
| Hybrid FTS5 + dense | <30ms | Best overall, covers both patterns |
| Graph traversal | <10ms | Best for "what's connected to X?" |

At personal scale, you can afford to run all three on every query and merge results.

---

## Capture Pipelines

The PKB is only as good as what gets into it. Common capture sources:

| Source | Tool | Note type |
|--------|------|----------|
| Web pages | Browser bookmarks + clipper | Literature note |
| Books / papers | Highlights export | Literature note |
| Voice memos | Whisper transcription | Fleeting → permanent |
| Meetings / calls | Transcript → summary | Project note |
| Conversations | Manual / AI-assisted | Fleeting |
| Your own ideas | Quick capture app | Fleeting → permanent |
| Decisions | Decision log | Permanent (never delete) |

**The capture → process pipeline**:
```
Capture (30s, no friction) → Daily inbox review (10min) → Weekly processing (30min)
```

The capture must be frictionless. The processing must be disciplined.

---

## PKB vs Second Brain vs Personal Context Engine

| System | What it stores | What it can do | What it cannot do |
|--------|--------------|---------------|-------------------|
| **PKB (static)** | Your notes and links | Search, browse, surface connections | Answer questions, synthesize, reason |
| **Second Brain (PARA)** | All your digital info | Organize for retrieval | Semantic query, temporal reasoning |
| **PKB + LLM (basic)** | Notes + embeddings | Semantic Q&A | Know your identity, remember sessions |
| **Personal Context Engine** | Notes + identity + episodic memory | Q&A + synthesis + proactive insight | (approaching) Full personal AI |

A personal knowledge base is the **foundation** of a personal context engine. Without a well-structured PKB, a personal context engine has nothing meaningful to ground its answers in.

---

## Related

- [[personal-context-engine|Personal Context Engine]] — what to build on top of the PKB
- [[karpathy-llm-os|Karpathy: LLM OS]] — the mental model for how LLMs use personal knowledge
- [[memory|Memory Systems]] — the technical layer that gives the engine persistent recall
- [[graph-rag|Graph RAG]] — how to make the link graph queryable
- [[indexing|Indexing Strategies]] — atomic claim extraction is a form of semantic indexing
