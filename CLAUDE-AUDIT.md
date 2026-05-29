# CLAUDE-AUDIT.md

> **Scope**: Documentation-only repository audit — no implementation code exists yet.
> **Audited by**: Claude (claude-sonnet-4-6)
> **Date**: 2026-05-29
> **Branch audited**: `main` (post-merge of `claude/repo-review-critique-B9TYM`)
> **Files audited**: 25 (README.md, .gitignore, LICENSE, all docs/)

---

## Addendum — Cross-Audit Findings (GEMINI-AUDIT.md)

After reviewing `GEMINI-AUDIT.md` (Antigravity AI / Gemini 3.5 Flash), two findings from that audit were confirmed as valid gaps not covered here. Both have been applied to the docs.

### GA01 — Air-Gap Paradox ✅ Applied

**Gemini finding**: NEXUS markets "No cloud. No data leaks." but the default setup pulls ~5.6 GB from the internet on first run. Industrial EPC sites and refineries in SEA frequently operate behind strict firewalls with no outbound internet. The online-first default is a direct contradiction of the air-gapped security claim for these clients.

**Applied to**:
- `docs/business/infrastructure.md` — added "Air-gap paradox" section with two deployment paths (online default + offline override), `docker-compose.offline.yml` spec, and `scripts/package-models.sh` description
- `docs/todo.md` — added offline bootstrap tasks to Phase 1

### GA02 — Hybrid SQLite FTS5 Index for Alphanumeric Precision ✅ Applied

**Gemini finding**: Dense embeddings (`multilingual-e5-large`) cannot reliably distinguish `AT-201` from `AT-202`, `CBL-001-HV-4` from `CBL-001-HV-3`, or similar exact alphanumeric identifiers. Semantic search on instrument tags, part numbers, and PO numbers produces wrong results with high confidence scores.

**Applied to**:
- `docs/modules/context-store/vector-store.md` — added full Hybrid Index section: SQLite FTS5 schema, query routing logic (`EXACT_PATTERN` regex), `fts_search()` and `hybrid_query()` interface additions, and FTS5 storage spec
- `docs/modules/query/query-engine.md` — updated query flow to use `hybrid_query()` as primary entry point; updated Mermaid diagram to show FTS5 routing
- `docs/todo.md` — updated context-store and query tasks to reflect hybrid index requirements

### Other valid Gemini findings (not yet applied — require design decisions)

| Finding | Status | Notes |
|---------|--------|-------|
| Conflict resolver false positives (complementary ≠ contradictory) | Open | Semantic similarity > 0.85 will flag `"AT-201 measures gas"` + `"AT-201 runs on 24V"` as a conflict. Needs a two-stage filter: similarity check, then explicit contradiction check. Add to Phase 2 conflict-resolver spec. |
| Intent detector embedding skew | Open | Appending role facet strings to the query before embedding shifts the vector direction. Log as open question for Phase 3 design. |
| Background ingestion worker | Open | FastAPI `BackgroundTasks` added to todo.md. Full Celery spec deferred to Phase 2+. |
| ChromaDB plain-text storage at rest | Open | No encryption on the SQLite file inside the Docker volume. Mitigation: full-disk encryption at VPS level (DigitalOcean volume encryption). Document in infrastructure.md. |

---

## Executive Summary

36 issues found across 10 categories (34 original + 2 from cross-audit). No implementation code exists yet, so all issues are in documentation, design specs, and planning files. **5 issues are critical** — they will cause implementation failures or rework if not resolved before coding starts.

### Severity Counts

| Severity | Count |
|----------|-------|
| 🔴 Critical | 5 |
| 🟠 High | 14 |
| 🟡 Medium | 10 |
| 🟢 Low | 5 |
| **Total** | **34** |

---

## Critical Issues (Fix Before Writing Code)

---

### C01 — Wrong Embedding Model Name Will Break First-Run Setup

**File**: `docs/business/infrastructure.md` line 72
**Severity**: 🔴 Critical
**Status**: Fixed in this audit

**Found**:
```
- `milkey-mouse/multilingual-e5-large` — embedding model
```

**Problem**: `milkey-mouse/` is not a valid Ollama namespace for this model. This would cause `docker-compose up` to fail on first run during the model pull step — the most visible failure point for a new client.

**Fix applied**: Changed to `intfloat/multilingual-e5-large` (the correct Ollama registry name).

**Related**: [docs/modules/context-store/vector-store.md](docs/modules/context-store/vector-store.md), [docs/decisions.md → D04](docs/decisions.md)

---

### C02 — Three Module Specs Are Missing (Blocks Phase 1 Implementation)

**Files**: `docs/modules/` — three planned modules have no spec
**Severity**: 🔴 Critical
**Status**: Open

The following modules appear in `docs/modules/INDEX.md` data flow diagram and `docs/todo.md` tasks, but have no spec file:

| Module | Expected path | Referenced in |
|--------|--------------|---------------|
| Metadata Tagger | `docs/modules/ingestion/metadata-tagger.md` | `todo.md` line 60, `modules/INDEX.md` data flow |
| Chunker (shared utils) | `docs/modules/ingestion/chunker.md` | `modules/INDEX.md` data flow diagram |
| Ingestion Pipeline | `docs/modules/ingestion/ingestion-pipeline.md` | `todo.md` line 61, `modules/INDEX.md` |

An implementer picking up Phase 1 has no spec to work from for the central orchestration layer.

**Recommended fix**:
- Create `docs/modules/ingestion/ingestion-pipeline.md` — orchestration inputs, outputs, error handling, and retry logic
- Create `docs/modules/ingestion/metadata-tagger.md` — what metadata is assigned, from where, defaults
- Clarify `chunker.py`: if chunking is entirely per-parser (which decisions.md D11 implies), remove the shared Chunker node from the data flow diagram. If there are shared chunking utilities, create a spec.

---

### C03 — API Error Responses Not Specified (Will Cause Rework)

**File**: `docs/modules/api/api.md`
**Severity**: 🔴 Critical
**Status**: Open

The API spec defines success responses but no error responses for any endpoint. A frontend developer building the chat UI and upload zone has no contract to code against for failure states.

**Missing**:
- What HTTP code does `POST /projects/{id}/query` return if project doesn't exist? (403? 404?)
- What format are all error responses? (`{"detail": "...", "status_code": N}` or something else?)
- What happens on partial ingestion failure (3 of 4 files succeed)?
- Async vs. blocking query response — how does the client know which mode it's getting?

**Recommended fix**: Add an error contract section to `docs/modules/api/api.md`:

```json
// Standard error response
{
  "error": "string",
  "code": "PROJECT_NOT_FOUND | UNAUTHORIZED | INGESTION_FAILED | ...",
  "detail": "string (human-readable)"
}
```

---

### C04 — JWT Token Lifecycle Unspecified (Security Gap)

**File**: `docs/modules/api/api.md`
**Severity**: 🔴 Critical
**Status**: Open

`POST /auth/refresh` is listed as an API route but has no specification. Critical questions unanswered:

- **Access token TTL**: How long is a JWT valid? (Unspecified — default could be infinite)
- **Refresh token TTL**: Not specified
- **Role change propagation**: If a PM demotes a user, does their existing JWT still grant PM-level access until it expires?
- **Logout / revocation**: No endpoint or mechanism. Once issued, a JWT cannot be invalidated without a blocklist.
- **Secret rotation**: No procedure if `JWT_SECRET` is compromised

In a self-hosted deployment, a JWT_SECRET leak means all sessions are permanently compromised until the secret is rotated and all users re-login. This needs a documented recovery path.

**Recommended fix**: Add to `docs/modules/api/api.md`:
```
Access token TTL: 8 hours
Refresh token: Not used in Phase 1 — re-login on expiry
Logout: DELETE /auth/session (adds token to in-memory blocklist until expiry)
Role change: Effective on next login (existing token honored until expiry)
JWT_SECRET rotation: Change in .env + docker-compose restart (forces all re-login)
```

---

### C05 — No Ingestion Error Handling Strategy

**File**: `docs/todo.md`, all ingestion module specs
**Severity**: 🔴 Critical
**Status**: Open

Individual parser specs mention failure modes (e.g., unrecognized WhatsApp format, empty PDF) but there is no system-wide answer to:

- **Batch upload failure**: If 4 files are uploaded and file 3 fails to parse, do files 1, 2, and 4 get committed to ChromaDB? Or is the entire batch rolled back?
- **Re-ingestion on crash**: If ingestion crashes halfway through a large PDF, does the system resume or restart from zero?
- **User visibility**: How does the PM know that one of their uploads failed?

The current spec implies silent partial failures — extremely dangerous for a product that markets itself on "trusted answers."

**Recommended fix**: Add to `docs/modules/ingestion/ingestion-pipeline.md` (to be created):
```
Error handling: Per-file isolation. Failure of one file does not block others.
Response: Partial success with per-file status and error reason.
Re-ingestion: Idempotent — re-running on the same file re-processes from scratch.
User notification: Failed files shown in ingestion status UI with specific error reason.
```

---

## High Issues

---

### H01 — LlamaIndex vs. Custom Pipeline Is "TBD" — Blocks Phase 1

**File**: `docs/modules/INDEX.md` line 125
**Severity**: 🟠 High
**Status**: Open — should be in open-questions.md

```
Ingestion framework | LlamaIndex (optional) or custom pipeline | TBD based on flexibility needs
```

This is a Phase 1 architectural decision. LlamaIndex imposes its own abstractions over chunking, embedding, and retrieval. Custom pipeline gives full control but more code to write. They are not easy to swap after the first sprint.

**Recommended fix**: Decide and log in `docs/decisions.md`. Given the custom document-type-specific chunking strategy (D11), a custom pipeline is likely the right call — LlamaIndex's default chunking would fight against D11. Add to `docs/open-questions.md` if still undecided.

---

### H02 — Vector Store Interface Has No Error Handling Contract

**File**: `docs/modules/context-store/vector-store.md`
**Severity**: 🟠 High

`VectorStore.upsert()` returns `None`. No exception types specified. No behavior defined for:
- ChromaDB unavailable (container down)
- Dimension mismatch on `upsert` (wrong embedding model used)
- `delete_collection()` called on non-existent collection
- `collection_stats()` return value — exact dict keys undefined

Every module that calls `VectorStore` will need to handle errors. Without a defined contract, each module will handle them differently (or not at all).

---

### H03 — Confidence Signal Definition Is Inconsistent

**Files**: `docs/modules/query/response-builder.md` line 90 vs. `docs/decisions.md` → D (no decision number for confidence)

`response-builder.md` defines confidence as:
```python
confidence = mean([chunk.similarity_score for chunk in top_k_chunks])
```

But `docs/critique/technical.md` T02 says: "cosine similarity of top-k retrieved chunks, LLM self-assessment, or citation coverage ratio."

Three options are listed in the critique but only one is implemented in the spec. The README says "confidence indicator based on source similarity" which matches only the cosine similarity approach.

**Recommended fix**: Lock the confidence calculation in `docs/decisions.md` as an explicit decision. The cosine similarity mean is the right choice for Phase 1 (no extra LLM call). LLM self-assessment can be Phase 2+ improvement.

---

### H04 — Conflict Resolver Cache Backend Unspecified

**File**: `docs/modules/context-store/conflict-resolver.md` line 79

```
This is expensive (extra LLM call). Cache results.
```

No cache backend specified. Options have very different complexity:
- In-memory dict: lost on restart, no persistence, simplest
- Redis: persistent, requires another Docker service
- Disk cache (shelve/diskcache): persistent, no new service

Given the Docker Compose setup and the target VPS, an in-memory cache with a TTL is probably right for Phase 2. Specifying Redis would mean adding a sixth Docker service unnecessarily.

---

### H05 — Authority Ranker Config Has No Storage or API Path

**File**: `docs/modules/context-store/authority-ranker.md` line 55–64

`authority_weight` is described as "configurable per project" but:
- Where is it stored? (No database schema defined yet)
- What API endpoint updates it?
- What's the default for new projects?
- Is there a UI control?

The API spec in `docs/modules/api/api.md` has no `PATCH /projects/{id}/config` endpoint.

---

### H06 — JWT Secret Generation Is Not a Todo Item

**File**: `docs/todo.md`
**Severity**: 🟠 High

`docs/decisions.md` D01 says JWT_SECRET is "generated per-installation." `docs/modules/api/api.md` says "generated at installation, stored in `.env`."

But `docs/todo.md` has no task for:
- Auto-generation of JWT_SECRET on first run if absent from `.env`
- Backup warning in setup guide
- Rotation procedure

Missing this task means it will either be forgotten or hardcoded to a default (a critical security vulnerability).

---

### H07 — No CORS, Rate Limiting, or Upload Security Spec

**File**: `docs/modules/api/api.md`
**Severity**: 🟠 High

API spec mentions CORS in a todo comment but does not specify:
- Allowed CORS origins (dev vs. prod)
- Rate limiting (per-user or per-IP)
- Max upload file size
- Allowed MIME types / extensions for document upload
- Filename sanitization (path traversal prevention)

An unsecured upload endpoint on a VPS accepting any file type of any size is a significant attack surface.

---

### H08 — Ollama Network Exposure Not Documented

**File**: `docs/modules/query/response-builder.md` line 114

Ollama listens on port 11434. In Docker Compose, if this is exposed on the host (`ports: - "11434:11434"`), any internet user can send inference requests and exhaust the CPU.

The spec assumes Docker internal networking but doesn't document it. The `docker-compose.yml` spec (not yet written) must not expose Ollama to the host network.

---

### H09 — WhatsApp Format Registry Not in Todo

**File**: `docs/todo.md`

`docs/bugs.md` PRE-001 identifies WhatsApp format fragility as a high-severity pre-implementation issue. The fix requires "a format version registry to track changes over time."

No task in `docs/todo.md` covers:
- Creating the format registry
- Test fixtures for each known format variant (iOS, Android, various locales)
- Detecting and reporting unrecognized formats loudly (not silently)

Without test fixtures for multiple WhatsApp export formats, the parser will be written against one format and silently fail on others.

---

### H10 — No Testing Tasks in Todo

**File**: `docs/todo.md`
**Severity**: 🟠 High

`docs/INDEX.md` line 82 notes "Tests: None — Set up after first module." But `docs/todo.md` has zero testing tasks. This means tests will be deferred indefinitely.

WhatsApp parser format detection (PRE-001) and the embedding dimension lock-in (PRE-002) are specifically things that can only be caught by tests — not by code review.

**Recommended additions to `docs/todo.md`**:
- Unit tests: WhatsApp parser (all format variants)
- Unit tests: Chunking logic per document type
- Integration tests: Ingestion pipeline end-to-end
- Integration tests: ChromaDB query and retrieval
- API tests: All routes with valid/invalid JWT

---

### H11 — chunk_id Derivation Algorithm Not Specified

**File**: `docs/modules/context-store/vector-store.md` line 52

```python
"chunk_id": str,  # SHA256 of content + source + timestamp
```

"content + source + timestamp" is ambiguous. Questions:
- Is it `SHA256(content + source_file)` or `SHA256(content + source_file + timestamp)`?
- If timestamp is included, re-ingesting the same message at a different time creates a new chunk_id — no deduplication.
- If content-only, an edited WhatsApp message gets the same ID and silently overwrites the original.

This is the deduplication contract. It must be unambiguous before writing the ingestion pipeline.

---

### H12 — Missing Task: Documentation for End Users

**File**: `docs/todo.md`

No tasks for user-facing documentation:
- Admin guide (how to create projects, upload documents, manage users)
- User guide (how to ask questions, interpret confidence and source labels)
- Troubleshooting guide (common errors, how to check `/health`)
- Backup and restore procedure (critical for self-hosted clients)

Without these, the first PM to deploy NEXUS has no reference material.

---

### H13 — LLM Inference Parameters Incomplete

**File**: `docs/modules/query/response-builder.md` lines 111–116

Specified: temperature (0.1), max_tokens (1024). Not specified:
- Top-p / top-k sampling
- Stop sequences (prevents LLM from continuing past the answer boundary)
- Request timeout (what happens if Ollama takes > 90s — common on cold CPU runs?)
- Retry logic (3 attempts? exponential backoff?)
- Behavior when answer is cut off at max_tokens

A 7B model on CPU can take 60–90 seconds for complex queries. Without a specified timeout and retry, the first slow query will cause a silent hang.

---

### H14 — No Disaster Recovery Procedure Documented

**File**: `docs/business/infrastructure.md`

Infrastructure.md mentions daily snapshots and a restore command but does not document:
- Where backups are stored (same VPS disk = no protection against disk failure)
- Off-site backup strategy (object storage, second location)
- Recovery time objective (RTO) and recovery point objective (RPO)
- Full restore procedure (step by step)
- Data retention compliance (any applicable local regulations in SEA)

A self-hosted client who loses their VPS has no documented recovery path.

---

## Medium Issues

---

### M01 — Missing Open Question: LicenseKey Validation Strategy

**File**: `docs/open-questions.md`

Phase 4 includes "license key mechanism" but no open question documents the design options or decision criteria. How is a key validated offline? How is revocation enforced on a self-hosted deployment? This should be in `docs/open-questions.md` before Phase 4 design starts.

---

### M02 — Missing Open Question: Multi-Project User Access Model

**File**: `docs/open-questions.md`

Decisions D05 and D06 specify one ChromaDB collection per project and JWT with `project_id`. But there is no decision about whether one user can access multiple projects. The `ProjectSwitcher` UI component implies yes, but the JWT carries a single `project_id`. If the user switches projects, do they get a new JWT? Does the JWT carry a list of allowed `project_id` values?

This must be resolved before building the project switcher (Phase 1).

---

### M03 — Missing Open Question: ChromaDB Scaling Limits

**File**: `docs/open-questions.md`

The reference spec is 16GB RAM. No documentation on when ChromaDB performance degrades (number of chunks, collection size), what the warning signs are, or what the migration path is if a client outgrows the spec.

---

### M04 — Frontmatter `status` Values Are Inconsistent Across Files

**Files**: Multiple module specs

Values in use: `not-implemented`, `spec only`, `active`, `open`. No schema defines what these mean or what the valid set is. An AI agent parsing frontmatter status will get inconsistent values across files.

**Recommended fix**: Add a frontmatter schema definition to `docs/INDEX.md` and standardize to: `not-implemented | active | resolved | archived`.

---

### M05 — No Defined Scope for `role: pm` vs. Admin

**File**: `docs/modules/api/api.md` role access table

The PM role is effectively the admin role (uploads docs, creates users, creates projects). There is no separation between "PM who manages their team" and "system admin who manages multiple PMs."

In a multi-PM deployment, can PM-A see PM-B's projects? This is undefined.

---

### M06 — Response Builder Prompt Template Language Not Specified

**File**: `docs/modules/query/response-builder.md` lines 91–103

The prompt template is English-only:
```
You are NEXUS, an engineering project assistant. Answer the question using ONLY the provided context.
```

If a user asks a question in Bahasa Indonesia and the retrieved chunks are also in Bahasa, the LLM will likely respond in English (since the system prompt is English). For SEA users, this breaks the product experience.

**Recommended fix**: The system prompt language should be configurable per installation, or auto-detect the language of the query and respond in the same language.

---

### M07 — `docker-compose.yml` Has No Spec Yet

**File**: `docs/todo.md`, `docs/business/infrastructure.md`

The compose file is the core deliverable of Phase 1 but has no spec. What services, what networks, what volume mounts, what environment variables does each service expose? The infrastructure.md gives a high-level list but nothing an implementer can code from.

---

### M08 — README Quick Start Is Non-Functional

**File**: `README.md` lines 195–210

The Quick Start commands assume files that don't exist (`docker-compose.yml`, `.env.example`). There is a status note that says "Implementation not started," but the Quick Start block appears before the note, meaning a reader who skims may try the commands and fail before reading the disclaimer.

**Recommended fix**: Move the status note to immediately before the Quick Start block, or replace the code block with a placeholder like `# Coming in Phase 1`.

---

### M09 — `.gitignore` Missing Node/Frontend and ChromaDB Patterns

**File**: `.gitignore`

The `.gitignore` is comprehensive for Python but missing entries for the planned React frontend and local development data:

```gitignore
# Missing: Node / React frontend
node_modules/
dist/
build/
.next/
out/
npm-debug.log*
yarn-error.log*

# Missing: Local data stores
data/
chroma_db/
*.db
*.sqlite*

# Missing: Docker local overrides
docker-compose.override.yml
.docker/
```

---

### M10 — No `.env.example` Task in Phase 1

**File**: `docs/todo.md` line 50

`.env.example` is listed as a Phase 1 task: `- [ ] .env.example with all required config documented`. But the task doesn't list what variables must be in it. Without a required-variables list, the `.env.example` will be incomplete and clients will hit missing-variable errors at runtime.

**Minimum required variables (to document)**:
```
JWT_SECRET=         # Auto-generated 32-byte random; MUST be set before use
OLLAMA_BASE_URL=http://ollama:11434
EMBEDDING_MODEL=intfloat/multilingual-e5-large
LLM_MODEL=qwen2.5:7b
CHROMADB_PATH=/app/data/chromadb
ALLOWED_ORIGINS=http://localhost:3000
ADMIN_EMAIL=        # First PM admin account
ADMIN_PASSWORD=     # First PM admin password (change after first login)
```

---

## Low Issues

---

### L01 — `planning.md` Is Now Redundant With The Doc System

**File**: `docs/planning.md`

The original `planning.md` was a single comprehensive file. It has been rewritten as a "lightweight summary" that links to the other files. However, the `docs/INDEX.md` already serves this purpose more completely. `planning.md` now has partial overlap with `INDEX.md` and adds minimal unique content.

**Recommended**: Either remove `planning.md` or differentiate it clearly (e.g., keep it as the "narrative history" of decisions and discussions, not a navigation document).

---

### L02 — `docs/modules/INDEX.md` Tech Stack Table Has "TBD" Cells

**File**: `docs/modules/INDEX.md` line 125

```
Ingestion framework | LlamaIndex (optional) or custom pipeline | TBD based on flexibility needs
```

No TBD entries should remain in a table that an implementer reads to decide what to install.

---

### L03 — `README.md` Has Two Consecutive Status Notes

**File**: `README.md` line 182 and line 211

The README mentions "Implementation not started" in two places. One is sufficient.

---

### L04 — `docs/bugs.md` Has No Created-Date Field in Bug Template

**File**: `docs/bugs.md`

The bug template includes `**Reported**: YYYY-MM-DD` but no `**Fixed in**` or `**Closed**: YYYY-MM-DD` field. The three pre-implementation bugs (PRE-001, PRE-002, PRE-003) have `Reported: 2026-05-29` but no closure tracking.

Minor — add `**Fixed in**: vX.X` to the template and to all three PRE issues (left blank until resolved).

---

### L05 — LICENSE Year/Name Should Be Verified

**File**: `LICENSE`

The LICENSE file contains `Copyright (c) 2026 Farhan Budiman`. Year 2026 is correct. Name should be verified as the intended copyright holder.

---

## Fixed in This Audit

| Issue | File | Fix |
|-------|------|-----|
| C01 — Wrong embedding model name | `docs/business/infrastructure.md` | Changed `milkey-mouse/multilingual-e5-large` → `intfloat/multilingual-e5-large` |

---

## Recommended Action Priority

### Before writing any code (Phase 1 pre-work)

1. **C02** — Create missing module specs: `ingestion-pipeline.md`, `metadata-tagger.md`, resolve chunker ambiguity
2. **C03** — Add error response contract to `docs/modules/api/api.md`
3. **C04** — Specify JWT token TTL, logout, and secret rotation in `docs/modules/api/api.md`
4. **C05** — Define ingestion error handling strategy
5. **H01** — Decide LlamaIndex vs. custom pipeline; log in `docs/decisions.md`
6. **M02** — Resolve multi-project access model for project switcher (Phase 1 blocker)
7. **H11** — Specify `chunk_id` derivation algorithm exactly
8. **M10** — List all required `.env` variables

### Before first client demo

9. **H07** — Add CORS, rate limiting, upload security spec to `docs/modules/api/api.md`
10. **H08** — Document Ollama network isolation in `docker-compose.yml` spec
11. **H09** — Add WhatsApp format registry and test fixtures to `docs/todo.md`
12. **H10** — Add testing tasks to `docs/todo.md`
13. **H13** — Complete LLM inference parameter spec (timeout, retry, stop sequences)
14. **M09** — Update `.gitignore` with Node/frontend and ChromaDB patterns

### Before first paying client

15. **C04** — Full JWT security spec (token expiry, revocation, secret rotation)
16. **H14** — Document full disaster recovery procedure
17. **H06** — Add JWT_SECRET auto-generation task to `docs/todo.md`
18. **M01** — Add license key validation design to `docs/open-questions.md`
19. **H12** — Add end-user documentation tasks to `docs/todo.md`

---

*Audit complete. All findings are documented above. No code was modified except the one critical defect fix noted in the Fixed section.*
