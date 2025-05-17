# Onboarding Guide – Crypto Arbitrage Platform

Welcome to the Crypto Arbitrage Platform! This guide will help you get started as a new user or developer.

## Quick Start (User)
1. **Install Dependencies**: Follow instructions in `README.md` for backend and dashboard setup.
2. **Configure API Keys**: Store your exchange API keys securely using Vault/KMS (never hardcode them).
3. **Start Services**:
   - Use `docker-compose` or Kubernetes manifests in `infra/` to launch all services.
   - The dashboard will be available at the address specified in your `.env` file.
4. **Explore the Dashboard**:
   - Each tab has tooltips and info icons for guidance.
   - Use the Controls tab for manual overrides (kill switch, etc.).
5. **Monitor Health**: Import the provided `GRAFANA_DASHBOARD.json` into your Grafana instance for live system monitoring.

## Quick Start (Developer)
1. **Clone the Repo** and review the `DEVELOPER_GUIDE.md` for architecture and extension instructions.
2. **Run Locally**:
   - Backend: `uvicorn services/api_gateway/main.py --reload`
   - Dashboard: `cd dashboard && yarn start`
3. **Testing**:
   - Backend: `pytest`
   - Frontend: `yarn test`
4. **Add Features**: Follow the code structure and always provide tooltips for new UI elements.

## Best Practices
- **Security**: Never commit secrets. Use environment variables and secret managers.
- **Documentation**: Update guides and tooltips for every new feature.
- **Monitoring**: Keep Grafana and Prometheus running for observability.

For more details, see `USER_GUIDE.md` and `DEVELOPER_GUIDE.md`.
