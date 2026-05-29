---
id: api
type: spec
status: not-implemented
phase: 1
last_updated: 2026-05-29
related:
  - ../INDEX.md
  - ../../decisions.md#d06
  - ../../decisions.md#d05
  - ../../decisions.md#d08
  - ../../todo.md
---

# Module: API Routes

> `backend/api/main.py` + `backend/api/routes/`

---

## Purpose

FastAPI application exposing all NEXUS functionality via REST endpoints. Handles JWT auth, project scoping, ingestion triggers, and query execution.

---

## Auth

All routes except `/auth/login` and `/health` require a valid JWT in the `Authorization: Bearer <token>` header.

JWT payload (per [decisions.md D06](../../decisions.md)):

```json
{
  "user_id": "string",
  "project_id": "string",
  "role": "pm | engineer | field_tech | procurement",
  "exp": 1234567890
}
```

JWT secret: generated at installation, stored in `.env` as `JWT_SECRET`. Never shared between installations.

---

## Route Map

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/login` | None | Exchange credentials for JWT |
| `POST` | `/auth/refresh` | JWT | Refresh token |

### Projects

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/projects` | JWT | List all projects for this installation |
| `POST` | `/projects` | JWT (pm) | Create a new project |
| `GET` | `/projects/{id}` | JWT | Get project details + stats |
| `DELETE` | `/projects/{id}` | JWT (pm) | Delete project + ChromaDB collection |
| `POST` | `/projects/{id}/switch` | JWT | Set active project in session |

### Ingestion

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/projects/{id}/ingest` | JWT (pm) | Upload file(s) for ingestion |
| `GET` | `/projects/{id}/ingest/status` | JWT | Get ingestion progress |
| `GET` | `/projects/{id}/documents` | JWT | List all ingested documents |
| `DELETE` | `/projects/{id}/documents/{doc_id}` | JWT (pm) | Remove document + its chunks |

### Query

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/projects/{id}/query` | JWT | Submit a query, get answer + sources |
| `GET` | `/projects/{id}/query/history` | JWT | Query history for this project |

### Users (Phase 3)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/users` | JWT (pm) | List users |
| `POST` | `/users` | JWT (pm) | Create user |
| `PATCH` | `/users/{id}/role` | JWT (pm) | Update user role |
| `DELETE` | `/users/{id}` | JWT (pm) | Deactivate user |

### System

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | None | Returns service health status |

---

## `/health` Response

```json
{
  "status": "ok",
  "services": {
    "chromadb": "ok",
    "ollama": "ok",
    "ollama_model": "qwen2.5:7b"
  },
  "version": "1.0.0"
}
```

---

## `/projects/{id}/query` Request & Response

**Request:**
```json
{
  "query": "What is the insulation rating of cable CBL-001-HV?",
  "n_results": 10
}
```

**Response:**
```json
{
  "answer": "Cable CBL-001-HV has XLPE insulation rated for 90°C...",
  "confidence": 0.84,
  "has_conflict": false,
  "sources": [
    {
      "content": "CBL-001-HV: 3-core, 4mm², XLPE insulation, 90°C...",
      "source_file": "Nexans_Datasheet_CBL001.pdf",
      "source_type": "pdf",
      "timestamp": "2024-01-15",
      "authority_level": 2,
      "label": null,
      "similarity_score": 0.91
    }
  ]
}
```

---

## Role-based Access

| Action | pm | engineer | field_tech | procurement |
|--------|----|----------|-----------|-------------|
| Upload documents | ✅ | ❌ | ❌ | ❌ |
| Delete documents | ✅ | ❌ | ❌ | ❌ |
| Query | ✅ | ✅ | ✅ | ✅ |
| Create users | ✅ | ❌ | ❌ | ❌ |
| Create projects | ✅ | ❌ | ❌ | ❌ |
| View project stats | ✅ | ✅ | ❌ | ❌ |

---

## Related

- [../../decisions.md → D05, D06, D08](../../decisions.md)
- [../context-store/vector-store.md](../context-store/vector-store.md)
- [../query/query-engine.md](../query/query-engine.md)
