# Crypto Arbitrage Platform (MVP Demo)

> **DISCLAIMER**: This is an _MVP‑level demo_, not production ready. Sensitive keys must be loaded via Vault, durable storage, real risk engine, and CI/CD hardening still required.

## Quick Start (Dev)

```bash
python -m venv .venv && source .venv/bin/activate  # windows: .venv\Scripts\activate
pip install -r requirements.txt
# start local Kafka + Redis via docker‑compose (not included here)

# 1️⃣ Market data
python services/market_data/collector.py
# 2️⃣ Spatial detector
python services/opportunity_engine/spatial.py
# 3️⃣ Risk manager
python services/risk_manager/basic.py
# 4️⃣ Execution engine (dry‑run)
python services/execution_engine/basic.py
```

## Structure
* `common/` – shared config, models, messaging helpers
* `services/` – modular microservices (market_data, opportunity_engine, …)
* `infra/` – Docker, k8s, Terraform (TBD)

## Roadmap
1. Portfolio/balance service
2. Full risk layers & kill‑switch
3. Monitoring dashboards
4. Kubernetes Helm charts + CI pipeline
5. Documentation with MkDocs
