---
id: docx-parser
type: spec
status: not-implemented
phase: 1
last_updated: 2026-05-29
related:
  - ../INDEX.md
  - ../../decisions.md#d11
  - ../../todo.md
---

# Module: DOCX Parser

> `backend/ingestion/parsers/docx_parser.py`

---

## Purpose

Parse Word documents (`.docx`) — primarily SOPs, site meeting minutes, and project reports. Preserves section hierarchy and numbered procedure steps as units.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Path to `.docx` file |
| `project_id` | `str` | Project context |
| `authority_level` | `int` | Caller-assigned (typically 3 for SOPs) |

---

## Outputs

List of `Chunk` objects with `source_type: "docx"` and `section_title: str` in metadata.

---

## Library

**python-docx** for `.docx` parsing.

---

## Chunking Strategy

Per [decisions.md D11](../../decisions.md): chunk by section heading, with numbered steps preserved as single units.

### Rules

1. Walk document paragraphs in order
2. When a `Heading 1` or `Heading 2` style is encountered, start a new chunk
3. The heading text becomes the chunk's `section_title`
4. Accumulate body paragraphs under that heading into the chunk
5. Numbered lists (SOP steps): keep the entire numbered sequence as one chunk, not split at each step number
6. Tables inside a section: each table row becomes a sub-chunk with the section title as context

### Example output

```
section_title: "3.2 Emergency Shutdown Procedure"
content: "1. Activate the ESD panel at the main control room. 2. Verify all process valves are in fail-safe position. 3. Notify the shift supervisor immediately. 4. Do not restart without written authorization from the HSE officer."
```

---

## Edge Cases

- Documents without headings: treat the entire document as one chunk (log a warning)
- Track changes / comments: strip revision marks, use the accepted text only
- Embedded images: skip (log as skipped, not as error)

---

## Related

- [pdf-parser.md](./pdf-parser.md)
- [../../decisions.md → D11](../../decisions.md)
