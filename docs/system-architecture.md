# AI Courtroom Companion – Justice for All

## 1) Full System Architecture Diagram (Layer-by-Layer)

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│                            CLIENT CHANNELS                                   │
│  Web (Next.js) | Mobile PWA | Kiosk | NGO Portal | Admin Console            │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                │ HTTPS / WSS (TLS 1.3)
┌───────────────────────────────▼───────────────────────────────────────────────┐
│                      FRONTEND EXPERIENCE LAYER                                │
│ Next.js App Router + React + i18n + WCAG 2.2 + RBAC UI                       │
│ Zustand (state), TanStack Query (server cache), WebSocket client             │
└───────────────────────────────┬───────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────────┐
│                            API GATEWAY LAYER                                 │
│ Kong / NGINX + OPA policy + JWT verify + rate limit + schema validation      │
│ Structured logs + trace propagation + request ID                              │
└───────┬────────────────────┬────────────────────┬─────────────────────────────┘
        │REST                │WSS                 │Async publish
┌───────▼────────────────────▼────────────────────▼─────────────────────────────┐
│                          MICROSERVICES MESH                                   │
│ 1. user-service (Auth, RBAC, consent, privacy mode)                          │
│ 2. document-service (upload, OCR orchestration, metadata)                    │
│ 3. nlp-service (simplification + multilingual + explainability)              │
│ 4. prediction-service (outcome forecast + bias checks + risk heatmap)        │
│ 5. blockchain-service (hashing, notarization, verification)                  │
│ 6. notification-service (SMS/Email/WhatsApp/Push, reminders)                │
│ 7. matchmaking-service (NGO/pro-bono ranking)                                │
│ Internal comms: REST + Kafka events (exactly-once semantic via idempotency)  │
└───────┬──────────────┬──────────────┬──────────────┬──────────────────────────┘
        │              │              │              │
┌───────▼───────┐ ┌────▼────────┐ ┌───▼────────┐ ┌───▼─────────────────────────┐
│ AI/OCR Layer  │ │Data Layer   │ │Cache Layer │ │Blockchain/Key Mgmt Layer     │
│ Tesseract/GCV │ │PostgreSQL   │ │Redis       │ │Polygon Amoy + Ethers.js      │
│ LLM + RAG     │ │pgvector     │ │BullMQ jobs │ │HSM/KMS + Vault               │
│ FAISS/Pinecone│ │S3 encrypted │ │sessions    │ │DocumentRegistry contract      │
└───────────────┘ └─────────────┘ └────────────┘ └──────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────────┐
│                      OBSERVABILITY & DEVOPS LAYER                            │
│ OpenTelemetry + Prometheus + Grafana + Loki + Tempo + SIEM                   │
│ CI/CD (GitHub Actions), IaC (Terraform), policy checks, SAST/DAST            │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2) Detailed Data Flow

### A. Document Upload → AI → Blockchain → Citizen Dashboard
1. Citizen uploads document (`PDF/JPG`) from frontend.
2. Frontend calls `POST /v1/documents` with multipart file + metadata + language.
3. API Gateway validates JWT, payload schema, and quotas.
4. `document-service` stores encrypted file in object storage, emits `document.uploaded`.
5. OCR worker consumes event, extracts text, emits `document.ocr.completed`.
6. `nlp-service` performs simplification + translation + legal term glossary.
7. `prediction-service` computes case likelihood + confidence + bias report.
8. `blockchain-service` stores SHA-256 hash on Polygon via smart contract.
9. Status updates are pushed to frontend through WebSocket events.
10. Frontend renders progressive steps, final simplified output, risk heatmap, and verification badge.

### B. Zero-Retention Privacy Mode
1. User toggles privacy mode during upload.
2. Persistent text storage is disabled.
3. Pipeline uses ephemeral queues and in-memory processing.
4. Only non-identifying audit proof + cryptographic hash is retained.

---

## 3) API Documentation

### Auth

#### `POST /v1/auth/login`
**Request**
```json
{
  "email": "citizen@example.org",
  "password": "StrongPassword#123",
  "deviceFingerprint": "sha256:..."
}
```

**Response**
```json
{
  "accessToken": "jwt-access-token",
  "refreshToken": "jwt-refresh-token",
  "expiresIn": 900,
  "role": "citizen",
  "mfaRequired": false
}
```

### Document Pipeline

#### `POST /v1/documents`
Multipart form-data: `file`, `language`, `jurisdiction`, `privacyMode`.

**Response**
```json
{
  "documentId": "doc_01JZ...",
  "status": "QUEUED",
  "pipelineId": "pipe_01JZ...",
  "estimatedSeconds": 75
}
```

#### `GET /v1/documents/{documentId}`
```json
{
  "documentId": "doc_01JZ...",
  "status": "SIMPLIFICATION_COMPLETED",
  "progress": 78,
  "steps": [
    { "name": "OCR", "state": "DONE" },
    { "name": "Simplification", "state": "DONE" },
    { "name": "Prediction", "state": "RUNNING" },
    { "name": "Blockchain", "state": "PENDING" }
  ]
}
```

#### `GET /v1/documents/{documentId}/result`
```json
{
  "summary": "Your tenancy notice gives you 30 days to respond...",
  "plainLanguageSections": [
    { "title": "What this means", "text": "..." }
  ],
  "voiceExplainerUrl": "https://cdn.../voice/doc_01...mp3",
  "prediction": {
    "outcome": "LikelySettlement",
    "score": 0.72,
    "confidence": 0.81,
    "biasFlags": ["regional_imbalance_low_support"]
  },
  "blockchain": {
    "status": "CONFIRMED",
    "network": "polygon-amoy",
    "txHash": "0xabc...",
    "contractAddress": "0x123...",
    "verificationUrl": "https://amoy.polygonscan.com/tx/0xabc..."
  }
}
```

### Matchmaking
#### `POST /v1/matchmaking/recommendations`
```json
{
  "documentId": "doc_01JZ...",
  "location": "Nairobi",
  "needs": ["family_law", "urgent_hearing"]
}
```

**Response**
```json
{
  "matches": [
    {
      "providerId": "ngo_11",
      "name": "Justice Bridge Foundation",
      "score": 0.91,
      "availability": "<24h",
      "languages": ["en", "sw"]
    }
  ]
}
```

### Notifications & Reminders
#### `POST /v1/reminders`
```json
{
  "documentId": "doc_01JZ...",
  "hearingDate": "2026-09-18T08:30:00Z",
  "channels": ["sms", "push"],
  "timezone": "Africa/Nairobi"
}
```

---

## 4) WebSocket Event Structure

Endpoint: `wss://api.justiceforall.global/v1/ws?token=<jwt>`

```json
{
  "event": "pipeline.progress",
  "timestamp": "2026-02-10T14:22:10.123Z",
  "correlationId": "pipe_01JZ...",
  "payload": {
    "documentId": "doc_01JZ...",
    "stage": "OCR",
    "progress": 35,
    "message": "Extracting text from page 7/20"
  }
}
```

Other events:
- `pipeline.partial_result` (streams incremental simplifications)
- `prediction.updated` (score recalculated)
- `blockchain.submitted` / `blockchain.confirmed`
- `notification.sent`
- `pipeline.error`

---

## 5) Authentication, State, Error Handling, Retry, Rate Limiting

### Authentication Flow
1. Login returns access token (15 min) + refresh token (7 days).
2. Access token in `Authorization: Bearer ...`.
3. Refresh via silent refresh endpoint.
4. Role claims: `citizen`, `lawyer`, `ngo_admin`, `court_admin`, `super_admin`.
5. Step-up MFA for admin/legal operations.

### Frontend State Management (Zustand + Query)
- **Zustand stores**:
  - `authStore`: user profile, token metadata, roles.
  - `pipelineStore`: active jobs, progress, ws events.
  - `uiStore`: locale, accessibility mode, toasts.
- **TanStack Query**:
  - caching GET endpoints
  - stale-while-revalidate
  - optimistic updates for reminders

### Error Handling Flow
- Gateway maps internal errors to user-safe envelopes:
```json
{
  "error": {
    "code": "DOC_OCR_TIMEOUT",
    "message": "We are processing your file. Please retry in a minute.",
    "retryable": true,
    "correlationId": "req_..."
  }
}
```

### Retry Logic
- Frontend retries retryable requests with exponential backoff: `1s, 2s, 4s, 8s` (max 4).
- Idempotency-Key required for create endpoints.
- Queue consumers use dead-letter topics and replay workflow.

### Rate Limiting
- Anonymous: `30 req/min/IP`
- Authenticated citizen: `120 req/min/user`
- Admin APIs: `60 req/min/user`
- Burst upload limit and adaptive challenge (captcha/risk engine).

---

## 6) Folder Structure (Frontend + Backend)

```text
ai-courtroom-companion/
├── apps/
│   ├── web/                          # Next.js frontend
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── documents/
│   │   │   ├── prediction/
│   │   │   ├── blockchain/
│   │   │   └── matchmaking/
│   │   ├── stores/
│   │   ├── services/
│   │   └── i18n/
│   └── admin-console/
├── services/
│   ├── api-gateway/
│   ├── user-service/
│   ├── document-service/
│   ├── nlp-service/
│   ├── prediction-service/
│   ├── blockchain-service/
│   ├── notification-service/
│   └── matchmaking-service/
├── packages/
│   ├── shared-types/                 # OpenAPI-generated DTOs
│   ├── observability/
│   ├── auth-sdk/
│   └── ui-kit/
├── contracts/
│   └── DocumentRegistry.sol
├── infra/
│   ├── terraform/
│   ├── kubernetes/
│   ├── helm/
│   └── github-actions/
└── docs/
    ├── system-architecture.md
    └── api-openapi.yaml
```

---

## 7) Database Schema (Core)

### PostgreSQL tables
- `users(id, role, email, phone, kyc_status, created_at)`
- `documents(id, user_id, jurisdiction, language, storage_url, privacy_mode, status, created_at)`
- `document_text_chunks(id, document_id, chunk_idx, text, embedding vector(1536))`
- `simplifications(id, document_id, locale, plain_text, explainability_json)`
- `predictions(id, document_id, outcome, score, confidence, bias_report_json, model_version)`
- `blockchain_records(id, document_id, hash, network, tx_hash, contract_address, confirmed_at)`
- `reminders(id, user_id, document_id, hearing_at, cron_expr, channels, last_sent_at)`
- `matchmaking_requests(id, user_id, document_id, criteria_json, top_result_json)`
- `audit_logs(id, actor_id, action, resource_type, resource_id, ip, user_agent, created_at)`

### Redis
- Session cache
- WS presence map
- Pipeline progress cache
- Token blocklist and short-lived OTP data

---

## 8) Smart Contract Code (Polygon-ready)

See `contracts/DocumentRegistry.sol` for production baseline with:
- Role-controlled notarization
- Hash uniqueness guard
- Verification method
- Event emission for backend listeners

---

## 9) AI Pipeline Flowchart (Explained)

```text
Upload -> OCR -> Preprocess/PII Masking -> Chunking -> Embeddings -> Vector Search
      -> RAG Context Builder -> Simplification LLM -> Explainability Layer
      -> Prediction Model -> Bias Detector -> Voice Explainer TTS -> Final Output
```

### Components
- **OCR**: multi-engine fallback (Tesseract then cloud OCR for low-quality scans).
- **RAG**: retrieves jurisdiction-specific acts, precedents, and templates.
- **Explainability module**: cites clauses used for each simplified statement.
- **Bias detector**: compares prediction confidence by demographic proxies (without storing sensitive raw PII).

---

## 10) Security, Compliance, and Privacy

- End-to-end encryption in transit (TLS 1.3) and at rest (AES-256).
- Envelope encryption using KMS/HSM-backed data keys.
- PII masking before model prompts.
- Row-level security in PostgreSQL for tenant/region isolation.
- Consent ledger + purpose limitation metadata for GDPR.
- Zero-retention mode for at-risk users.
- Smart contract audit checklist (reentrancy, access control, event integrity).
- Model governance: versioning, drift checks, human override path.

---

## 11) DevOps & International Deployment Plan

### Docker & Runtime
- Each microservice: distroless image, non-root user, read-only FS.
- Sidecars: OTel collector + secret injector.

### CI/CD
1. Lint + unit tests + contract tests
2. SAST + dependency scan + IaC scan
3. Build/push signed images (cosign)
4. Deploy to staging via Helm
5. Synthetic + smoke tests
6. Manual approval for production
7. Progressive rollout (blue/green or canary)

### Cloud Architecture (AWS/GCP)
- Kubernetes (EKS/GKE) multi-AZ.
- Managed PostgreSQL, Redis, Kafka.
- Object storage for documents.
- Global CDN + WAF.
- Multi-region active-passive with disaster recovery RPO < 15m, RTO < 60m.

### Horizontal Scaling
- HPA by CPU/RPS and queue lag.
- Separate autoscaling profiles for OCR, NLP, and prediction workers.
- Kafka partitions by jurisdiction and workload class.

### Monitoring & Logging
- Prometheus metrics + Grafana dashboards.
- Loki for logs, Tempo for traces.
- SLOs: upload success, pipeline latency, tx confirmation time.
- Alerting to PagerDuty + Slack.

---

## 12) Advanced Innovation Modules

1. **AI Legal Voice Explainer**
   - Real-time TTS streams simplified output in local language and dialect.
2. **Deadline Reminder Engine**
   - Rule + cron-based scheduler with time zone aware reminders.
3. **NGO/Pro Bono Matchmaking AI**
   - Ranking model uses geography, urgency, specialization, and language.
4. **Risk Heatmap Visualization**
   - Aggregated risk by region/case type with drill-down charts.
5. **Bias Detection Layer**
   - Ongoing fairness metrics + alerting + governance dashboard.

---

## 13) 2-Minute International Hackathon Pitch Script

> "Today, millions lose legal rights simply because legal language is impossible to understand. We built **AI Courtroom Companion – Justice for All** to close that gap at national scale.
>
> A citizen uploads a court notice. In seconds, our AI pipeline extracts text, simplifies legal jargon into plain language, translates it, and explains next steps in voice. In parallel, we predict likely case outcomes with confidence and fairness checks, so users can make informed decisions—without replacing human judges or lawyers.
>
> Every document is cryptographically notarized on Polygon, creating a tamper-proof verification trail trusted by courts, NGOs, and legal aid partners. Real-time status updates are streamed to the dashboard, so users always know what is happening.
>
> This is not a demo-only prototype. We designed a secure microservices architecture with API gateway controls, role-based access, zero-retention privacy mode, end-to-end encryption, and full observability. It is cloud-native, horizontally scalable, and internationally deployable.
>
> Beyond simplification, we schedule hearing reminders, match users to pro bono lawyers, visualize legal risk heatmaps, and continuously monitor model bias. The result is a platform that makes justice understandable, accessible, and verifiable for everyone.
>
> **AI Courtroom Companion** is where legal-tech meets public trust—built for governments, NGOs, and millions of citizens who deserve equal access to justice." 
