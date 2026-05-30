---
id: orchestration-frameworks
type: research
status: active
last_updated: 2026-05-30
tags: [llamaindex, langchain, langgraph, haystack, dspy, frameworks, orchestration]
related:
  - ./INDEX.md
  - ./retrieval.md
  - ./memory.md
  - ./combinations.md
---

# Orchestration Frameworks

> **TL;DR**: LlamaIndex for retrieval-heavy pipelines. LangGraph for stateful agents. Haystack for auditability and production ops. DSPy for prompt optimization research. Custom for high-stakes, latency-sensitive production.

---

## Performance Benchmark (Same Agentic RAG Pipeline, 2025)

| Framework | Overhead latency | Tokens/query | Download (monthly) |
|-----------|----------------|-------------|-------------------|
| **DSPy** | ~3.5 ms | ~2.0k | Low |
| **Haystack** | ~5.9 ms | ~1.57k | ~394K |
| **LlamaIndex** | ~6.0 ms | ~1.60k | ~5M |
| **LangChain** | ~10 ms | ~2.40k | Very high |
| **LangGraph** | ~14 ms | ~2.03k | Bundled with LangChain |

Answer correctness is near-identical across frameworks on the same pipeline. The differentiation is **orchestration overhead** and **token consumption**.

---

## LlamaIndex (0.10+)

Retrieval-centered. The most widely used RAG framework by download volume (~5M/month).

**First-class support for:**
- Document ingestion (SimpleDirectoryReader, connectors for S3, Notion, Confluence, SharePoint, etc.)
- Index types: VectorStoreIndex, KnowledgeGraphIndex, PropertyGraphIndex, SummaryIndex
- Query engines, chat engines, sub-question decomposition
- LlamaParse for high-quality PDF/document parsing (commercial)

**LlamaIndex 0.10** restructured into modular packages (`llama-index-core` + plugins). This reduced base install size and improved composability.

**When to use:**
- Your primary problem is document ingestion and retrieval
- You need pre-built connectors to data sources
- You want property graph or knowledge graph support without building from scratch

**When not to use:**
- Complex stateful agent loops with cycles (LangGraph is better)
- Teams that need tight LangSmith observability integration

---

## LangChain / LCEL / LangGraph

### LCEL (LangChain Expression Language)
Declarative chain composition using the `|` pipe operator. Type-safe, supports streaming and async natively.

```python
chain = prompt | llm | output_parser
result = await chain.ainvoke({"query": "What is AT-201?"})
```

### LangGraph
Production-grade extension for **stateful multi-actor graphs**:
- Supports cycles (required for ReAct agents that retry)
- Persistent state with checkpoints
- Human-in-the-loop interruption points
- Subgraph composition for multi-agent systems
- Built-in support for streaming, background execution

**The go-to choice for agentic RAG workflows as of 2025.**

### LangSmith
Evaluation and tracing layer. Integrates natively with LangGraph for:
- Production observability (trace every chain execution)
- Version comparison (A/B test prompt changes)
- Evaluation datasets and feedback collection

**When to use LangGraph:**
- Complex agent workflows with conditional branching
- Human-in-the-loop approval flows
- Multi-agent systems where agents communicate
- Any stateful long-running session

---

## Haystack (deepset)

Pipeline-first, declarative component model:

```yaml
# Serializable to YAML — auditable, version-controllable
components:
  - name: retriever
    type: InMemoryBM25Retriever
    params:
      top_k: 20
  - name: reranker
    type: CohereRanker
  - name: generator
    type: OpenAIGenerator
```

Components are type-checked, serializable, and independently testable. Lowest token usage in benchmarks. Strong enterprise adoption in Europe.

**When to use:**
- Teams needing auditability: every pipeline component is traceable
- Regulated environments (the YAML serialization creates an audit trail)
- Production systems where ops teams need to inspect and modify pipelines without touching Python code

---

## DSPy (Stanford, 2023–2025)

Rather than writing prompts manually, you define **input/output signatures** and DSPy optimizes prompts automatically:

```python
class RAGSignature(dspy.Signature):
    """Answer questions using retrieved context."""
    context = dspy.InputField(desc="Relevant documents")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="Concise factual answer")

class RAG(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought(RAGSignature)
```

DSPy optimizers (MIPRO, BootstrapFewShot) automatically find the best prompt configuration given labeled training examples.

**Strengths:**
- Dramatically reduces prompt engineering effort
- Compositional: DSPy modules chain like neural network layers
- Optimization is measurable: you define a metric, DSPy maximizes it

**Production maturity gaps:**
- Observability, cost tracking, and deployment tooling are explicitly listed as gaps in the DSPy roadmap (expected in DSPy 3.0)
- Optimized prompts can be brittle across model versions
- Black-box optimization makes debugging harder

**When to use:**
- Research pipelines where maximizing a metric is the goal
- Teams willing to invest in optimization setup upfront
- When you have labeled evaluation data and want the best possible prompt automatically

---

## Custom Pipelines

For high-stakes production systems, many teams build minimal custom orchestration:
- Vector database SDK directly (Qdrant, Weaviate)
- Embedding API (OpenAI, Cohere, or local model via Ollama)
- LLM API
- Use LlamaIndex or LangChain only for specific components (e.g., LlamaIndex just for the retriever, custom code for everything else)

**When to use:**
- Full control over every latency-sensitive path
- Avoiding framework abstractions that add overhead
- When framework versions would introduce breaking changes at critical production moments

---

## Framework Decision Matrix

```
What's your primary problem?
├── Document ingestion + retrieval pipeline
│   └── LlamaIndex
├── Stateful agents with complex control flow
│   └── LangGraph
├── Auditability, regulated env, YAML pipelines
│   └── Haystack
├── Research, prompt optimization, measurable benchmarks
│   └── DSPy
└── Maximum performance, full control
    └── Custom + specific SDKs
```

---

## Related

- [[retrieval|Retrieval Methods]] — LlamaIndex and LangChain both have retriever abstractions
- [[memory|Memory Systems]] — LangMem integrates with LangGraph; Mem0 integrates with LlamaIndex
- [[combinations|Best Stack by Use Case]] — framework recommendations per use case
- [[graph-rag|Graph RAG]] — LlamaIndex PropertyGraphIndex; LangChain + Neo4j
