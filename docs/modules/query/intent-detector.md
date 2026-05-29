---
id: intent-detector
type: spec
status: not-implemented
phase: 3
last_updated: 2026-05-29
related:
  - ./query-engine.md
  - ../../decisions.md#d06
  - ../../todo.md
---

# Module: Intent Detector

> `backend/query/intent_detector.py`

---

## Purpose

Classify what facet of an answer the user actually wants, based on their role and query text. Same question from different roles should surface different information.

---

## Phase

Phase 3. In Phase 1 and 2, all users get the same answer. In Phase 3, the query engine applies role-aware filtering and the response builder frames the answer differently per role.

---

## Example

**Query**: "What is the spec for cable CBL-001-HV?"

| Role | Answer facet |
|------|-------------|
| Procurement engineer | Part number, vendor, unit price, lead time, MOQ |
| Field technician | Diameter, insulation type, temperature rating, hazard zone (ATEX/IECEx) |
| Project manager | Budget line, approval status, delivery ETA, PO number |
| Engineer | Cross-section, current capacity, voltage rating, installation standard |

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `query_text` | `str` | Raw user query |
| `role` | `str` | From JWT: `pm` \| `engineer` \| `field_tech` \| `procurement` |

---

## Outputs

```python
@dataclass
class Intent:
    role: str
    facets: list[str]         # e.g., ["price", "vendor", "lead_time"]
    query_modifier: str       # Appended to query before embedding
                              # e.g., "procurement price vendor lead time"
    metadata_filter: dict     # ChromaDB where filter if applicable
```

---

## Implementation Strategy

### Phase 3a — Rule-based
Simple role → facet mapping. Add `query_modifier` string to the query before embedding. Fast, no extra LLM call.

```python
ROLE_FACETS = {
    "procurement": ["price", "vendor", "lead time", "part number", "quantity"],
    "field_tech":  ["installation", "dimension", "hazard", "zone", "rating", "diameter"],
    "pm":          ["status", "approval", "budget", "ETA", "PO"],
    "engineer":    ["specification", "standard", "calculation", "rating", "capacity"],
}
```

### Phase 3b — LLM-assisted (optional)
If rule-based produces poor results, add a lightweight classification call to the LLM to identify the primary intent before retrieval.

---

## Related

- [query-engine.md](./query-engine.md)
- [../../decisions.md → D06](../../decisions.md)
