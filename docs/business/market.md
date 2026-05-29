---
id: market
type: narrative
status: active
last_updated: 2026-05-29
related:
  - ./model.md
  - ./infrastructure.md
  - ../decisions.md
  - ../open-questions.md#q1
---

# Market & Target Users

---

## Primary Market

**Southeast Asia — Indonesia, Malaysia, Philippines**

Why SEA:
- WhatsApp is the dominant business communication tool (not Slack, not Teams)
- EPC and IoT industries are growing rapidly with infrastructure investment
- Strong data residency sensitivity — cloud tools with overseas servers create compliance concerns
- Price-sensitive market but EPC firms have real budgets for operational tools
- Underserved by enterprise software (most tools are priced and designed for US/EU markets)

---

## Target Industries

### 1. EPC (Engineering, Procurement, Construction)

Project teams managing large-scale infrastructure builds. Typical projects: power plants, refineries, water treatment facilities, manufacturing lines.

**Pain**: Knowledge scattered across WhatsApp groups (informal), PDF drawings (formal), Excel BOMs (procurement), and Word SOPs (operations). New team members have no way to access institutional knowledge. Handovers lose context.

**Decision makers**: Project Manager, HSE Manager, Document Controller

**End users**: Field technicians, procurement engineers, site engineers

---

### 2. Industrial IoT Integrators

Teams integrating sensors, PLCs, and control systems. Node-RED flows, P&ID drawings, and device datasheets are their primary documents.

**Pain**: Multiple vendors, multiple datasheet revisions, informal configuration decisions in WhatsApp, no single source of truth for "which firmware version is running on FT-101."

**Decision makers**: Integration PM, Lead Engineer

---

### 3. HSE & CEMS Compliance Teams

Health, Safety, Environment and Continuous Emissions Monitoring System teams. Work with regulatory documents, SOP compliance records, and incident logs.

**Pain**: Audits require proving that the correct SOP version was followed. Documents are scattered across email attachments and shared drives. Finding the right version of a document under audit pressure is time-consuming and error-prone.

**Decision makers**: HSE Manager, Compliance Officer

---

## User Roles Within a Deployment

| Role | What they do in NEXUS | Authority to upload? |
|------|-----------------------|---------------------|
| PM (admin) | Uploads documents, creates projects, manages users | Yes |
| Field Technician | Asks questions about equipment specs and procedures | No |
| Procurement Engineer | Asks about BOMs, vendors, pricing, lead times | No |
| Site Engineer | Asks about technical specs, calculations, standards | No |

---

## Multilingual Reality

EPC teams in Indonesia and Malaysia write in a mix of Bahasa Indonesia and English. A single WhatsApp message might read:

> "Sudah cek P&ID rev C. Cable AT-201 perlu diganti karena spec-nya tidak match dengan datasheet Yokogawa yang terbaru."

This is standard code-switching. Any system using an English-only embedding model will have poor recall on these messages. This is why `multilingual-e5-large` was chosen over `nomic-embed-text`.

See [open-questions.md Q1](../open-questions.md) — WhatsApp language confirmation pending.

---

## Competitive Landscape

| Tool | Approach | Why clients would choose NEXUS instead |
|------|----------|----------------------------------------|
| Notion AI | Cloud, generic, no EPC-specific context | Self-hosted, no data leak risk, EPC-specific ingestion |
| Microsoft Copilot | Requires M365 ecosystem, expensive, cloud | No vendor lock-in, self-hosted, no ongoing SaaS fee |
| Confluence + LLM | Requires structured content migration, cloud | Ingests existing unstructured docs (WhatsApp, PDFs) as-is |
| Custom ChatGPT wrapper | Cloud API, data sent to OpenAI | Air-gapped, all data stays on client VPS |
| Generic RAG (in-house) | Requires engineering team to build and maintain | Pre-built, documented, maintained by NEXUS builder |

**Core differentiators to emphasize in sales:**
1. WhatsApp as a first-class knowledge source (competitors ignore this)
2. Conflict resolution with authority labels (no other tool does this for EPC)
3. Fully air-gapped — data never leaves the client's server
4. Role-aware answers (procurement vs. field tech vs. PM get different facets)

---

## Related

- [model.md](./model.md)
- [infrastructure.md](./infrastructure.md)
- [../critique/business.md](../critique/business.md)
