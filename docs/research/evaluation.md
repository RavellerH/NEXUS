---
id: evaluation-frameworks
type: research
status: active
last_updated: 2026-05-30
tags: [evaluation, ragas, ares, trulens, deepeval, metrics, rag]
related:
  - ./INDEX.md
  - ./combinations.md
  - ./overview.md
  - ./retrieval.md
---

# Evaluation Frameworks

> **TL;DR**: Start with RAGAS in your development loop. Add TruLens for production monitoring. Use DeepEval for CI/CD gates. Manual evaluation (golden sets) is mandatory for domain-specific accuracy.

---

## Why Evaluation Is Non-Negotiable

A context engine without evaluation is a black box. You cannot know:
- Whether your retrieval is finding the right chunks
- Whether your LLM is using those chunks faithfully
- Whether answer quality is degrading after a code change
- Whether one chunking strategy is better than another for your corpus

Most practitioners who skip evaluation discover problems first through angry users.

---

## The Four Frameworks

### RAGAS

The de facto standard for RAG pipeline evaluation. Paper: Arxiv 2309.15217.

**Core metric set:**

| Metric | What it measures | Requires ground truth? |
|--------|-----------------|----------------------|
| **Faithfulness** | Is the answer grounded in the retrieved context? | No (LLM-evaluated) |
| **Answer Relevancy** | Does the answer address the question? | No |
| **Context Precision** | Are retrieved chunks relevant (signal-to-noise)? | Yes |
| **Context Recall** | Was all necessary information retrieved? | Yes |
| **Factual Correctness** | Is the answer factually correct? | Yes (reference answer) |

**Extended 2025 metric set** includes: Noise Sensitivity, Context Entities Recall, Multimodal Faithfulness, Multimodal Relevance, Topic Adherence, Tool Call Accuracy, Tool Call F1, Agent Goal Accuracy, Response Groundedness.

**Limitation**: RAGAS uses LLMs as judges for reference-free metrics. LLM judges (GPT-4 class) correlate ~0.8 Spearman with human judgment — good but not perfect. Results can be gamed by prompts that sound relevant but are incorrect.

**When to use**: Development loop, A/B testing pipeline changes, regression testing after changes.

---

### ARES

Research-grade automated evaluation. Approach:

1. Generates synthetic query-passage pairs from your corpus
2. Fine-tunes task-specific classifier "judges" (not LLM API calls)
3. Produces statistically confident interval estimates

**Advantages:**
- Cheaper per evaluation once fine-tuned judges are trained
- Supports local execution (no API cost)
- Produces confidence intervals, not just point estimates

**Disadvantages:**
- Setup overhead: requires fine-tuning, which requires labeled data
- Less general than RAGAS (judges are domain-specific)

**When to use**: Mature production systems where you have a labeled evaluation set and need cost-efficient continuous evaluation.

---

### TruLens

Evaluation + tracing combined. Feedback functions for groundedness and relevance. Supports:
- OpenTelemetry for production traces
- Version comparison (compare V1 vs. V2 of your pipeline)
- Execution-flow inspection (see exactly what retriever returned, what reranker re-ordered)
- Integration with LangChain and LlamaIndex

**When to use**: Production monitoring of a live RAG system. Best for continuous quality surveillance after deployment.

---

### DeepEval

Pytest-style evaluation with a catalog of RAG and hallucination metrics:

```python
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

@pytest.mark.parametrize("test_case", test_cases)
def test_rag_pipeline(test_case):
    metric = FaithfulnessMetric(threshold=0.8)
    assert_test(test_case, [metric])
```

**Features:**
- CI/CD integration (runs in GitHub Actions)
- Synthetic test generation
- Red-teaming and adversarial test cases
- Custom metric definitions

**When to use**: Automated quality gates in deployment pipelines. Catches regression before it reaches users.

---

## What Metrics Actually Matter in Production

### The Essential Five

| Priority | Metric | How to measure |
|----------|--------|---------------|
| 1 | **End-to-end answer accuracy** | Human-annotated golden set; most important, hardest to automate |
| 2 | **Retrieval recall@k** | Did the right chunks appear in top-k? (golden chunks or RAGAS Context Recall) |
| 3 | **Faithfulness / hallucination rate** | RAGAS or LLM judge; key for trust |
| 4 | **Latency p95** | User-facing SLA (typically &lt;3s for synchronous) |
| 5 | **Cost per query** | Retrieval + reranking + generation + memory |

### Metrics That Sound Good But Are Insufficient

| Metric | Why it's insufficient |
|--------|----------------------|
| BLEU / ROUGE | Surface-form metrics; poor correlation with factual accuracy in open-domain QA |
| Perplexity | Measures fluency, not correctness |
| LLM preference (GPT-4 judge alone) | Biased toward verbose, confident-sounding answers regardless of accuracy |

---

## Evaluation Data Strategy

### Golden Set Construction

A golden evaluation set should contain:
- Representative queries from real users (or realistic proxies)
- Ground-truth answers (written by domain experts, not LLM-generated)
- Ground-truth source chunks (which specific passages contain the answer)

**Minimum size**: 50–100 examples for initial evaluation; 500+ for reliable A/B testing.

**For domain-specific deployments** (legal, medical, EPC engineering), there are no good public benchmarks. You must build your own golden set. This requires domain expert annotation effort — budget 1–2 hours per expert per 20 examples.

### Synthetic Data Generation

For rapid bootstrapping before real user queries exist:

```python
# RAGAS synthetic data generation
from ragas.testset import TestsetGenerator
generator = TestsetGenerator.from_llm(llm, embedding_model)
testset = generator.generate_with_llamaindex_docs(documents, test_size=50)
```

Synthetic data is useful for regression testing after code changes. It's not a substitute for real-user golden sets for accuracy assessment.

---

## Evaluation in the Context Engine Lifecycle

```
Development
  ├── RAGAS on synthetic test set → pick best chunking / embedding configuration
  ├── DeepEval in CI/CD → catch regressions on every pull request
  └── Manual spot-check of 20 examples per change

Pre-launch
  ├── Golden set (50–100 expert-annotated examples)
  ├── End-to-end accuracy measurement
  └── Latency + cost profiling under load

Production
  ├── TruLens tracing → catch quality degradation
  ├── User feedback signals (thumbs up/down, explicit corrections)
  └── Periodic golden set refresh with real user queries
```

---

## Domain-Specific Notes

| Domain | Automated eval sufficiency | Notes |
|--------|--------------------------|-------|
| Customer support FAQ | Good | RAGAS faithfulness correlates well with user satisfaction |
| Legal contract review | Insufficient | Human expert review mandatory; errors have legal consequences |
| Healthcare / medical | Insufficient | Life-safety — requires clinical validation loop |
| EPC engineering | Moderate | Instrument tag precision testable; specification accuracy needs expert review |
| Code search | Good | Functional correctness is testable with code execution |
| Personal knowledge mgmt | Good | User is their own judge |

---

## Related

- [[combinations|Best Stack by Use Case]] — evaluation recommendations per domain
- [[retrieval|Retrieval Methods]] — retrieval recall@k is the most impactful metric to optimize first
- [[indexing|Indexing Strategies]] — RAGAS context precision reveals whether your chunking produces clean signal
