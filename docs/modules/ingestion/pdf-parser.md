---
id: pdf-parser
type: spec
status: not-implemented
phase: 1
last_updated: 2026-05-29
related:
  - ../INDEX.md
  - ./pid-parser.md
  - ../../decisions.md#d11
  - ../../todo.md
---

# Module: PDF Parser

> `backend/ingestion/parsers/pdf_parser.py`

---

## Purpose

Extract text, tables, and instrument tags from PDF files. Used for vendor datasheets, manuals, SOPs, and P&ID drawings. Routes P&ID files to enhanced tag extraction. Applies section-aware chunking to preserve document structure.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Path to `.pdf` file |
| `project_id` | `str` | Project context |
| `authority_level` | `int` | Caller-assigned (e.g., 2 for vendor datasheet, 3 for SOP) |
| `doc_type` | `str` | `"datasheet"` \| `"sop"` \| `"manual"` \| `"pid"` \| `"other"` |

---

## Outputs

List of `Chunk` objects with `source_type: "pdf"` and optionally `instrument_tags: list[str]` in metadata.

---

## Library

**PyMuPDF (`fitz`)** — handles text extraction, table detection, and page layout analysis.

---

## Chunking Strategy

Per [decisions.md D11](../../decisions.md):

| PDF type | Strategy |
|----------|----------|
| Text-heavy (manuals, datasheets) | By paragraph, respecting section headers. Section header becomes chunk title. |
| Table-heavy (BOMs, spec sheets) | Each table row as one chunk. Column headers prepended: `"Column1: value, Column2: value, ..."` |
| P&ID drawings | Route to [pid-parser.md](./pid-parser.md) for tag extraction |

**Page boundary handling**: If a paragraph spans two pages, merge it into one chunk. Do not split mid-sentence at page breaks.

---

## P&ID Routing

If `doc_type == "pid"` or if the filename contains common P&ID indicators (`P&ID`, `PID`, `piping`, `instrument`), route to `pid_parser.py` instead of standard text extraction.

---

## Known Issues

- Scanned PDFs (image-only, no text layer) produce empty extraction. PyMuPDF returns no text. Phase 1: log a warning and skip. Phase 4: add OCR via Tesseract or similar.
- Two-column layouts can produce interleaved text when extracted linearly. PyMuPDF's `sort=True` flag helps but does not fully resolve this for complex layouts.

---

## Related

- [pid-parser.md](./pid-parser.md)
- [excel-parser.md](./excel-parser.md)
- [../../decisions.md → D11](../../decisions.md)
