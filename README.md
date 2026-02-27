# AI Courtroom Companion – Justice for All

Production-ready, globally deployable legal-tech platform scaffold with frontend, API gateway, microservices, AI model registry, blockchain contract, and cloud-native deployment assets.

## Included Modules

### 1) Product Apps
- `apps/web` (Next.js): citizen-facing dashboard with login, file upload, live WebSocket pipeline updates, and AI result viewer.

### 2) Core Platform Services
- `services/api-gateway`: auth validation, rate limiting, route aggregation, error envelopes, WebSocket broadcast.
- `services/user-service`: login/JWT issuance.
- `services/document-service`: upload intake + pipeline metadata.
- `services/nlp-service`: legal language simplification endpoint.
- `services/prediction-service`: outcome scoring + risk heatmap + bias flags.
- `services/blockchain-service`: notarization payload generation.
- `services/notification-service`: deadline reminders.
- `services/matchmaking-service`: NGO / pro-bono recommendations.

### 3) AI Model Registry
- `models/simplifier/manifest.json`
- `models/predictor/manifest.json`
- `models/embeddings/manifest.json`
- `models/bias-detector/manifest.json`

### 4) Blockchain
- `contracts/DocumentRegistry.sol` for immutable hash notarization and verification.

### 5) Infra & Delivery
- `docker-compose.yml` for full local stack boot.
- `.github/workflows/ci.yml` for compile/build validation.
- `infra/k8s/api-gateway-deployment.yaml` for Kubernetes baseline.
- `docs/system-architecture.md` and `docs/api-openapi.yaml`.

## Run

```bash
docker compose up --build
```

Frontend: `http://localhost:3000`
Gateway: `http://localhost:8080`

## Quality Gates

```bash
make pycheck
```
