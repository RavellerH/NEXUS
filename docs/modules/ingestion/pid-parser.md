---
id: pid-parser
type: spec
status: not-implemented
phase: 1
last_updated: 2026-05-29
related:
  - ./pdf-parser.md
  - ../INDEX.md
  - ../../decisions.md#d09
  - ../../todo.md
---

# Module: P&ID Parser

> `backend/ingestion/parsers/pid_parser.py`

---

## Purpose

Extract instrument tags and associated context from P&ID (Piping & Instrumentation Diagram) drawings in PDF format. Phase 1 uses regex-based extraction from the PDF text layer. Phase 4 adds OCR for scanned/image-only P&IDs.

This module was moved from Phase 4 to Phase 1 — see [decisions.md D09](../../decisions.md).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Path to `.pdf` P&ID drawing |
| `project_id` | `str` | Project context |
| `authority_level` | `int` | Caller-assigned (typically 2 — approved drawing) |

---

## Outputs

List of `Chunk` objects with:
- `source_type: "pid"`
- `instrument_tags: list[str]` — all tags found on the page
- `content: str` — surrounding text context for each tag

---

## Phase 1 — Regex Extraction

### Tag patterns (ISA 5.1 standard)

```python
TAG_PATTERN = re.compile(
    r'\b([A-Z]{1,2})([A-Z]{1,2})-(\d{3,4}[A-Z]?)\b'
)
```

| Part | Meaning | Example |
|------|---------|---------|
| First letter(s) | Measured variable | `A`=Analysis, `F`=Flow, `L`=Level, `P`=Pressure, `T`=Temperature |
| Second letter(s) | Function | `T`=Transmitter, `C`=Controller, `V`=Valve, `I`=Indicator |
| Number | Loop number | `201`, `101A` |

### Common tags to recognize

`AT`, `FT`, `FIC`, `FCV`, `LT`, `LIC`, `LCV`, `PT`, `PIC`, `PCV`, `TT`, `TIC`

### Chunking for P&IDs

Each unique instrument tag + its surrounding text (±200 characters) = one chunk.

```python
# Example chunk content
"AT-201: Analyzer Transmitter on Stream 4 outlet. Connected to FIC-202. 
 Range: 0-100% CH4. Alarm high: 85%. Vendor: Yokogawa EXA202."
```

---

## Phase 4 — OCR Extraction

For scanned P&IDs with no text layer:
- Use `pytesseract` or `easyocr` to extract text from image
- Apply same regex patterns to OCR output
- Confidence threshold: skip low-confidence OCR results

---

## Known Limitations

- Regex will miss non-standard tag formats used by some vendors
- Cannot extract spatial relationships between instruments (which instruments are on the same line)
- Scanned P&IDs produce zero output in Phase 1 — log a warning

---

## Related

- [pdf-parser.md](./pdf-parser.md)
- [../../decisions.md → D09](../../decisions.md)
- [../query/query-engine.md](../query/query-engine.md)
