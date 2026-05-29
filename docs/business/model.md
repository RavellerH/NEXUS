---
id: business-model
type: narrative
status: active
last_updated: 2026-05-29
related:
  - ./market.md
  - ./infrastructure.md
  - ../open-questions.md
  - ../decisions.md#d01
  - ../decisions.md#d02
  - ../critique/business.md
---

# Business Model

---

## What We're Selling

A self-hosted AI context engine packaged as a deployable Docker Compose bundle. The client receives the software, deploys it on their own VPS, and runs it independently. The builder does not manage client infrastructure.

---

## Why Self-Hosted (Not SaaS)

SaaS means owning client uptime. One crash or bad deployment stops product development. At solo-founder stage, on-call burden kills momentum. Self-hosted shifts infrastructure responsibility to the client. The product is the software, not the service.

**The tradeoff**: Blame doesn't disappear — it shifts from "your service is down" to "my update broke something." Mitigated by one-command updates, a `/health` endpoint, and a clear support boundary in the license.

See [decisions.md D01](../decisions.md).

---

## License Model

### Recommended: Annual License Key

| Stage | Flow |
|-------|------|
| Purchase | Client pays → receives license key |
| Activation | Key entered during setup; valid for 12 months |
| During license period | Full product + all updates released in that period |
| After expiry — renews | Pays again → new key → continues getting updates |
| After expiry — doesn't renew | Product continues working on the version they have; no new features or fixes |

**Why this works:**
- Recurring revenue — renewal cohort grows as clients accumulate
- No "subscription" framing (software license, not ongoing service)
- No hostage dynamic — non-renewing clients aren't cut off
- Clean update model — updates are included in the license period
- Clients sharing a key risk only getting out-of-sync updates (honor system for Phase 1; technical enforcement in Phase 4)

### Tiering (Phase 4)

| Tier | Installations | Projects | Price (estimate) |
|------|--------------|---------|-----------------|
| Solo PM | 1 | Up to 5 | TBD |
| Team | 1 | Unlimited | TBD |
| Agency | Up to 5 | Unlimited | TBD |

**Note**: Pricing discussion deferred until MVP is built and validated with first user.

---

## Sales Process

The target buyer (PM at an EPC firm in SEA) does not buy software by clicking a "Buy Now" button. Expected sales flow:

1. **Discovery**: WhatsApp DM, LinkedIn, or referral from another PM
2. **Demo**: Zoom/Google Meet — show a working deployment with their type of documents
3. **Trial**: Offer a 30-day trial on the client's own VPS (builder does the setup)
4. **Invoice**: Send an invoice to their company's accounts department (bank transfer, not credit card)
5. **Onboarding**: Deliver license key + setup guide + first ingestion walkthrough

---

## Distribution Format

**Phase 1 (current)**: Private GitHub repo access — client clones, runs `docker-compose up`. Trust-based.

**Phase 4**: Private Docker Hub image + license key validation. Client pulls image via license-authenticated credentials.

See [open-questions.md Q2](../open-questions.md).

---

## Setup Add-on (Recommended)

Offer a paid "first deployment" service. Builder (or a designated person) does the initial VPS setup, Docker install, model pull, and first document ingestion.

- Removes the biggest adoption barrier for non-technical PMs
- Reveals real-world setup failure modes before they become support issues
- Justifies a higher overall price point

For first 3–5 clients: do it free. Learn what breaks. Then charge for it.

---

## Open Questions

- [Q3: One-time vs annual license confirmed?](../open-questions.md)
- [Q4: Setup service included?](../open-questions.md)
- [Q5: Individual or company buyer?](../open-questions.md)

---

## Related

- [market.md](./market.md)
- [infrastructure.md](./infrastructure.md)
- [../critique/business.md](../critique/business.md)
- [../decisions.md → D01, D02](../decisions.md)
