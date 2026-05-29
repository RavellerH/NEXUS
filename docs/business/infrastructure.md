---
id: infrastructure
type: narrative
status: active
last_updated: 2026-05-29
related:
  - ./model.md
  - ../decisions.md#d10
  - ../modules/INDEX.md
---

# Infrastructure & Deployment

---

## Deployment Model

NEXUS runs entirely on the client's own VPS. The builder ships a Docker Compose bundle. The client runs it on hardware they own or rent. No data leaves their server.

---

## Official Supported Spec

**DigitalOcean Singapore — 16GB RAM, 8 vCPU Droplet (~$96/mo)**

| Component | RAM usage | Notes |
|-----------|-----------|-------|
| Qwen2.5-7B Q4_K_M (Ollama) | ~5 GB | CPU inference |
| ChromaDB | ~500 MB–2 GB | Grows with document count |
| FastAPI backend | ~200 MB | |
| React frontend (nginx) | ~50 MB | |
| OS + Docker overhead | ~1–2 GB | |
| **Total** | **~8–10 GB** | Leaves ~6 GB headroom on 16GB |

Why DigitalOcean:
- PM-friendly control panel (easy to manage billing, resize, snapshot)
- Singapore region minimizes latency for SEA clients
- Reliable uptime, well-documented
- Easy to resize if load grows

---

## Alternative VPS Options

| Provider | Region | Spec | Cost/mo | Best for |
|----------|--------|------|---------|----------|
| DigitalOcean | Singapore | 16GB RAM, 8 vCPU | ~$96 | Default recommendation |
| Vultr | Singapore | 16GB RAM, 6 vCPU | ~$80 | Budget-conscious clients |
| IDCloudHost | Jakarta | 16GB RAM | ~Rp 600K | Indonesian data residency requirement |
| Biznet Metro | Jakarta | Configurable | ~Rp 800K+ | Enterprise Indonesian clients |

---

## Services in Docker Compose

```yaml
services:
  api:          # FastAPI backend
  frontend:     # React app served via nginx
  chromadb:     # Vector database
  ollama:       # LLM + embedding inference

volumes:
  nexus_chromadb:   # Named volume — prevents accidental deletion
  nexus_ollama:     # Model weights cache
```

### First-run model pull (online)

On first `docker-compose up`, the `ollama` service automatically pulls:
- `qwen2.5:7b` — LLM for answer generation (~4.5 GB)
- `intfloat/multilingual-e5-large` — embedding model (~1.1 GB)

This requires internet access on first run only. Subsequent runs are fully offline.

---

### Air-gap paradox — Offline bootstrap support

> **Critical**: NEXUS markets itself as "No cloud. No data leaks." But the default setup pulls ~5.6 GB from the internet on first run. Industrial EPC sites, refineries, and CEMS facilities in SEA often sit behind strict firewalls with no outbound internet access. The online-first default directly contradicts the air-gapped security claim for these clients.

**Two deployment paths must be supported:**

**Path A — Online (default)**
```bash
# Requires outbound internet on first run
docker-compose up -d
# Ollama pulls models automatically (~5.6 GB, ~10–20 min depending on connection)
```

**Path B — Offline (air-gapped)**
```bash
# Run once on a machine WITH internet to pre-package models
./scripts/package-models.sh
# Produces: nexus-models.tar (~5.6 GB) and nexus-images.tar

# Transfer both tarballs to the air-gapped VPS (USB, secure file transfer)
# Then on the air-gapped server:
docker load -i nexus-images.tar
docker run --rm -v nexus_ollama:/root/.ollama alpine tar -xf /mnt/nexus-models.tar -C /
docker-compose -f docker-compose.yml -f docker-compose.offline.yml up -d
```

**What `docker-compose.offline.yml` does**: Overrides the Ollama service to skip model pull on startup and use the pre-loaded volume instead.

**Tasks required** (see [todo.md → Phase 1](../../todo.md)):
- `scripts/package-models.sh` — pulls models on internet machine, tars them
- `docker-compose.offline.yml` — override file disabling auto-pull
- Setup guide section: "Deploying on Air-Gapped Networks"

---

## Response Time Expectations (CPU-only)

| Query complexity | Expected time |
|-----------------|---------------|
| Simple factual (tag lookup) | 5–15s |
| Moderate (multi-chunk synthesis) | 20–45s |
| Complex (conflict resolution) | 45–90s |

**Design implication**: The UI should show a loading state and not time out before 120 seconds. For Phase 3, consider an async queue with a push notification when the answer is ready — allows the user to do other things while waiting.

---

## Backup Strategy

```
/app/data/chromadb/   ← ChromaDB data directory
/app/data/backups/    ← Daily snapshots
```

Daily cron job (inside the `api` container or a sidecar):
```bash
tar -czf /app/data/backups/chromadb_$(date +%Y-%m-%d).tar.gz /app/data/chromadb/
```

Retain last 7 days. Client is responsible for copying backups to external storage (object storage, external drive).

**Restore procedure**:
1. Stop all containers
2. Extract snapshot to `/app/data/chromadb/`
3. Restart containers

---

## Update Process

One-command update (to be documented in setup guide):

```bash
docker-compose pull
docker-compose up -d
```

This pulls the latest images and restarts containers with zero data loss (volumes are persistent).

**Version support policy**: Latest version only. Clients on older versions who need support must update first.

---

## Network & Security

- NEXUS listens on `localhost` by default
- Client is responsible for placing a reverse proxy (nginx, Caddy) in front with TLS
- Recommended: Caddy with automatic Let's Encrypt for HTTPS
- No ports exposed to the internet except 80/443 (via reverse proxy)
- JWT secret must be rotated on first install (generated automatically if not set)

---

## Related

- [../decisions.md → D10](../decisions.md)
- [../modules/INDEX.md](../modules/INDEX.md)
- [model.md](./model.md)
