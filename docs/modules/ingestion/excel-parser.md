---
id: excel-parser
type: spec
status: not-implemented
phase: 1
last_updated: 2026-05-29
related:
  - ../INDEX.md
  - ../../decisions.md#d11
  - ../../todo.md
---

# Module: Excel Parser

> `backend/ingestion/parsers/excel_parser.py`

---

## Purpose

Parse Excel (`.xlsx`) and CSV files — primarily Bill of Materials (BOMs), procurement sheets, and measurement logs. Each row becomes a chunk with column headers prepended for context.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Path to `.xlsx` or `.csv` file |
| `project_id` | `str` | Project context |
| `authority_level` | `int` | Caller-assigned |
| `sheet_name` | `str \| None` | Specific sheet to parse; if None, parse all sheets |

---

## Outputs

List of `Chunk` objects with `source_type: "excel"`.

---

## Library

**openpyxl** for `.xlsx`. Python built-in `csv` module for `.csv`.

---

## Chunking Strategy

Per [decisions.md D11](../../decisions.md): each data row = one chunk, with column headers prepended.

### Format

```
BOM Item: Cable, Part Number: CBL-001-HV, Specification: 3-core 4mm², Vendor: Nexans, Quantity: 250m, Unit Price: Rp 45.000
```

### Rules
- Skip entirely empty rows
- Skip header rows (row 1 is assumed to be the header)
- If a cell contains a newline, replace with space
- Numeric cells: include the unit if present in the header (e.g., `"Price (Rp)"` → prepend `"Price: "`)
- Multi-sheet workbooks: prefix each chunk with the sheet name

---

## Edge Cases

- Merged cells: unmerge and duplicate the value into each merged cell before processing
- Formula cells: evaluate the formula result, not the formula string (openpyxl `data_only=True`)
- Empty sheets: skip with a log warning

---

## Related

- [pdf-parser.md](./pdf-parser.md)
- [../../decisions.md → D11](../../decisions.md)
