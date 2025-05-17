# Deployment Guide – Crypto Arbitrage Platform

## Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Kafka, Redis (auto-launched with compose)
- HashiCorp Vault (recommended for secrets)

## Quick Start (Dev)
```bash
git clone <repo>
cd Crypto\ arbitrage
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start infra and all services
cd infra
docker compose up --build
```

- API Gateway: http://localhost:8000
- Prometheus metrics: http://localhost:9000

## Kubernetes (Production)
- See infra/k8s/ for Helm charts and manifests (TBD)
- Secrets: configure Vault/KMS integration and mount as env vars
- Use external managed Kafka/Redis for HA

## CI/CD
- Recommended: GitHub Actions or GitLab CI
- Lint: `mypy`, `black`, `ruff`
- Test: `pytest`, `pytest-asyncio`
- Integration: run all services with test config, replay historical data

## Adding New Exchanges/Strategies
- Add exchange API keys to config.yaml or Vault
- Implement new connector in `services/market_data/`
- Register new strategy in `opportunity_engine/`
- Update Docker/K8s manifests as needed
