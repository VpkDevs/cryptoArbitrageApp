# Developer Guide – Crypto Arbitrage Platform

## Architecture Overview
- **Microservices**: Each core function (data collection, opportunity detection, execution, risk management, portfolio, API gateway, dashboard) is a separate service.
- **Kafka**: Used for real-time message streaming between services.
- **Redis**: Used for fast state storage and caching.
- **FastAPI**: Main backend API gateway.
- **React (Chakra UI)**: Dashboard frontend.

## Adding a New Exchange
1. Implement a new connector in `services/market_data/` using `ccxtpro`.
2. Add exchange-specific config to the `.env` and Kubernetes manifests.
3. Update the opportunity engines to include the new exchange in their search logic.
4. Add tests for data collection and execution.

## Adding a New Strategy
1. Create a new module in `services/opportunity_engine/` (e.g., `momentum.py`).
2. Implement the detection logic and ensure it emits opportunities to Kafka.
3. Update documentation and dashboard tooltips if new terms are introduced.

## Extending the Dashboard
- Add new React components in `dashboard/src/components/`.
- Use `TooltipInfo` for all new user-facing fields.
- Add API endpoints in FastAPI as needed.

## Testing & CI/CD
- Use `pytest` for backend tests, `jest`/`react-testing-library` for frontend.
- All code must pass linting and tests before deploy.
- CI/CD pipeline is configured for automated testing and deployment.

## Security & Secrets
- API keys/secrets are never hardcoded. Use Vault/KMS and reference via environment variables.
- Review all code for security issues before merging.

## Monitoring & Observability
- Use the provided Grafana dashboard JSON for system monitoring.
- Prometheus scrapes all microservices for metrics.

## Documentation
- Update `USER_GUIDE.md` and this guide for any new features or changes.
- All new user-facing features must include tooltips or inline guides.
