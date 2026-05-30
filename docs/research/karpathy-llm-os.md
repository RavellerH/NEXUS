---
id: karpathy-llm-os
type: research
status: active
last_updated: 2026-05-30
tags: [karpathy, llm-os, operating-system, context-window, personal-ai, software-2, eureka-labs]
related:
  - ./INDEX.md
  - ./memory.md
  - ./frameworks.md
  - ./personal-context-engine.md
  - ./personal-knowledge-base.md
  - ./overview.md
---

# Karpathy: LLM as Operating System

> **TL;DR**: Andrej Karpathy's LLM OS mental model reframes the question from "how do I use this chatbot?" to "how do I architect a cognitive system?" LLM = CPU. Context window = RAM. Weights = slow storage. Tools = I/O devices. Personal knowledge = the filesystem. This framing explains why context engines are necessary — and what "personal AI" must eventually become.

---

## The Mental Model: LLM as Operating System

In his November 2023 talk "Intro to Large Language Models," Karpathy presented the LLM OS framing. It reframes how LLMs fit into a broader computing stack:

```
┌────────────────────────────────────────────────────────┐
│                    LLM OPERATING SYSTEM                │
├────────────────────────────────────────────────────────┤
│  CPU            → LLM (the reasoning engine)           │
│  RAM            → Context window (limited, precious)   │
│  Hard disk      → Weights (trained, slow to update)    │
│  Keyboard/Mouse → Text / multimodal input              │
│  Display        → Generated text output                │
│  Internet       → Retrieval / web browsing tools       │
│  Running apps   → Agent subprocesses, code interpreter │
│  Filesystem     → Vector stores, documents, memory     │
│  User           → The human in the loop                │
└────────────────────────────────────────────────────────┘
```

**Why this matters**: The OS analogy makes clear that a "chatbot" is not the right mental model. A chatbot has no persistent state, no filesystem, no processes. An OS has all of these. The LLM OS framing is the mental model for context engines.

---

## Unpacking the Analogy

### CPU = LLM

The LLM is the processor. It:
- Takes input (context window contents) and produces output
- Has a fixed clock speed (inference speed per token)
- Does not store state between calls — it is stateless per forward pass
- Is expensive to upgrade (fine-tuning = new CPU)

Key Karpathy insight: **"The weights are like a vague dream of the internet."** The LLM has compressed world knowledge into its parameters, but this knowledge is frozen, approximate, and cannot be queried like a database.

### RAM = Context Window

The context window is the most precious resource in the LLM OS. Everything the model can "see" and reason about in a single inference call must fit in RAM.

- **Modern context windows**: 128K–1M tokens (GPT-4o, Claude 3.x, Gemini 1.5)
- **Effective use**: Not all context is equal. Where information appears in the context matters (beginning and end are better-attended than middle — the "lost in the middle" problem)
- **The RAM bottleneck**: Unlike real RAM, you cannot just add more context tokens without cost. Each doubling of context length quadratically increases attention computation.

**Karpathy's framing of the context stuffing problem**: "The central challenge of AI engineering is figuring out what to put in RAM at the right time." This is the definition of context engine work.

### Weights = Slow Storage

The model weights are like a hard disk that:
- Has enormous capacity (trillions of compressed facts)
- Cannot be directly read or written (only accessed through inference)
- Is updated only through fine-tuning (slow, expensive, risky)
- Cannot be reliably "edited" — you can't delete a fact from weights

**Key implication**: Don't rely on weights for current knowledge. The internet, your documents, and your personal history must come through the context window — not from weights. This is why RAG exists: weights cannot reliably answer "what is the current status of AT-201?"

### Tools = I/O Devices

Modern LLMs with tool use have:
- Internet access (web search, retrieval)
- Code execution (Python interpreter)
- File read/write
- External APIs (databases, calendars, communication tools)

Karpathy: "An LLM that can use tools is qualitatively different from one that cannot. It can affect the world, not just describe it."

### The LLM OS in Practice

Karpathy describes the emerging architecture of capable AI systems as:

```
LLM (reasoning core)
├── Tools (internet, code, files)
├── Long-term memory (vector store, database)
├── Short-term memory (context window, summarizer)
├── Planning module (decompose task → subtasks)
└── Reflection module (critique own outputs)
```

This is the architecture of a context engine with an agent loop.

---

## Software 1.0 → 2.0 → 3.0

Karpathy's three-phase model of software evolution:

- **Software 1.0** (2017 blog post): Programmer writes explicit rules. Deterministic logic. Python, C++.
- **Software 2.0**: Neural networks trained on data. The weights are the program. Programmer defines loss function; gradient descent writes the code.
- **Software 3.0** (2024–2025): Natural language prompts are the program. The context window is RAM. The LLM is the interpreter. What you include in context is the executable specification.

> "Classic software 1.0 is code we write. Software 2.0 is code written by optimization. Software 3.0 is code written in English."

For knowledge systems this means: a personal context engine does not hardcode rules about your preferences, decisions, or thinking style. It **learns** them from your data. The context engine is Software 3.0 applied to personal knowledge — and the bottleneck has shifted from *writing code* to *managing context*.

---

## Karpathy's Personal AI Vision

### The "Chief of Staff" Concept

In multiple interviews and talks (2023–2025), Karpathy has described the personal AI he wants to build/use:

> "I want an AI that has access to everything I've ever written, thought, or experienced. That can draft emails in my voice, recall what I decided about a problem six months ago, connect a new idea to something I read two years ago."

He calls this a "Chief of Staff AI" — not just a tool you query, but an AI that knows your context continuously and can act on it proactively.

**Key properties of the Chief of Staff AI**:
1. **Persistent identity** — knows who you are without being re-explained each session
2. **Voice matching** — writes in your style, not a generic style
3. **Decision memory** — knows your past decisions and their context
4. **Proactive synthesis** — connects things you haven't asked to connect
5. **Scope awareness** — knows what you're currently working on without being told

### What He Actually Uses — The LLM Wiki

In early 2026, Karpathy published his actual personal knowledge system as a GitHub Gist (`gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`). This is the most concrete publicly available spec of a personal context engine from a leading AI researcher.

**Three-layer architecture:**
1. **Raw Sources** — Immutable articles, papers, images. The LLM reads them but never modifies them. Drop a web article here and the system processes it.
2. **Wiki Layer** — LLM-generated and LLM-maintained Markdown files (entity pages, concept summaries, cross-references). *"You rarely ever write or edit the wiki manually. It's the domain of the LLM."*
3. **Schema Layer** — A `CLAUDE.md` configuration file establishing structural conventions and operational workflows for the LLM.

**Core operations:**
- **Ingest**: Drop a new source → LLM reads it, updates relevant wiki pages, creates cross-references, files the new knowledge
- **Query**: Ask a question → LLM searches wiki pages, synthesizes answer with citations, optionally files the answer as a new page
- **Lint**: Periodic health checks — contradictions, stale claims, orphan pages, data gaps

**Scale**: His current research wiki: ~100 articles, ~400,000 words on a single domain. Longer than most PhD dissertations. *Written by no one directly.*

**Tools**: Obsidian (visual frontend), Obsidian Web Clipper (converts web articles to Markdown), `qmd` (hybrid BM25 + vector search for large vaults), Claude Code (the LLM that maintains the wiki).

**The Vannevar Bush connection**: Karpathy explicitly connects this to **"As We May Think"** (Vannevar Bush, The Atlantic, 1945) — Bush's 1945 concept of the Memex, a personal, curated knowledge store with associative trails. The Memex was a desk-sized machine. Karpathy's version runs on a laptop. The LLM solves the maintenance problem Bush couldn't: *"The LLM handles that."*

**Other workflow elements:**
- **Voice → text pipeline** — captures ideas via voice memo, transcribed, filed as fleeting notes
- **Cursor** — AI-assisted coding environment; his primary development tool
- **Heavy use of LLM APIs** for thinking-partner tasks, not just chatting
- **Eureka Labs** (his 2024 startup) — AI-native education; AI that teaches you the way Karpathy himself would teach

### On Memory and Context

Karpathy on the memory problem (paraphrased from various talks):

> "The context window is the bottleneck. Everything important needs to be in context at query time. The intelligence is in the model; the knowledge is in what you put in front of it."

> "The sleeping/waking analogy: the model's weights are like long-term memory formed during sleep (training). The context window is working memory. RAG is like checking your notes."

> "When AI has persistent, personal, long-term memory — when it truly knows you — it becomes qualitatively different."

---

## The LLM OS and Context Engines

The LLM OS framing directly motivates the context engine architecture:

| LLM OS component | Context engine equivalent |
|-----------------|--------------------------|
| RAM loading | Context assembly — what gets retrieved and placed in context |
| Filesystem | Vector store + graph store + personal knowledge base |
| I/O | Document ingestion, tool calls, API integration |
| Process management | Agent orchestration (LangGraph, LlamaIndex workflows) |
| Memory management | What to keep in context, what to summarize, what to retrieve |
| OS kernel | The LLM itself (Qwen, Claude, GPT-4) |

**The context engine is the operating system layer of the LLM OS.** The LLM cannot be an OS by itself — it needs the filesystem, I/O, and memory management layer. That layer is the context engine.

---

## Software 1.0 Knowledge Systems vs LLM OS Knowledge Systems

| | Traditional PKB | LLM OS Knowledge System |
|--|----------------|------------------------|
| Query model | Keyword / tag | Natural language |
| Answer model | Returns links | Synthesizes and explains |
| Knowledge update | Manual note-writing | Auto-ingested from all sources |
| Cross-source synthesis | Manual (you connect) | Automatic (LLM connects) |
| Temporal reasoning | Browse by date | "What did I think about X 3 months ago?" |
| Proactive | Never | Surfaces relevant past when you work |
| Voice | Not native | Native input path |

The LLM OS enables a knowledge system that:
1. Knows everything you've captured
2. Can reason about it in response to natural questions
3. Synthesizes across sources without you guiding the synthesis
4. Gets smarter as your knowledge base grows
5. Matches your vocabulary and thinking style

---

## Karpathy's Influence on Context Engine Design

### What he gets right

1. **Context window is the bottleneck**: Every context engine decision ultimately comes down to "what should be in context?" The framing of context assembly as the core engineering problem is correct.

2. **Weights cannot serve as a reliable knowledge store**: This is why RAG, context engines, and personal knowledge systems exist. Weights hallucinate, become stale, and cannot be updated.

3. **Tools change everything**: An LLM without tools is a text transformer. An LLM with tools is an agent that can query your documents, run calculations, and affect the world.

4. **Personal AI requires persistent memory**: Stateless chatbots are a transitional phase. The mature form of AI assistance is a system that knows you over time.

### What he has not yet solved (publicly)

1. **The capture problem**: How do you get everything into the system without friction?
2. **The ontology problem**: How does the AI build a model of your personal concepts, not just your words?
3. **The privacy problem**: Persistent personal memory raises serious data ownership questions.
4. **The authority problem**: When the AI's memory of what you decided conflicts with what you now believe, who wins?

These are the open design problems for personal context engines.

---

## Key References

| Source | Year | Key idea |
|--------|------|---------|
| "Intro to Large Language Models" (talk) | 2023 | LLM OS framing, weights as slow storage |
| "State of GPT" (Microsoft Build talk) | 2023 | GPT-4 capabilities, fine-tuning vs prompting |
| "Software 2.0" (blog post) | 2017 | Neural nets replacing manually written code |
| Twitter / X threads | 2023–2025 | Personal AI, voice-to-notes, Chief of Staff AI concept |
| Eureka Labs announcement | 2024 | AI-native education, AI "teaching assistant" |

---

## Related

- [[personal-context-engine|Personal Context Engine]] — what a personal context engine is and how it's built
- [[personal-knowledge-base|Personal Knowledge Base]] — the curated store the LLM OS draws on
- [[memory|Memory Systems]] — how persistent memory is implemented technically
- [[overview|Context Engine Overview]] — context engine as the OS layer of the LLM OS
- [[frameworks|Orchestration Frameworks]] — the tools for building LLM OS workflows
