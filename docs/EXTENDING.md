# Extending the Crypto Arbitrage Platform

## Adding a New Exchange
1. Add credentials to `config.yaml` or your Vault secrets store.
2. Implement a new connector in `services/market_data/collector.py` (use ccxtpro or custom WebSocket handler).
3. Ensure the symbol normalization matches your strategies.
4. Add exchange to Docker/K8s manifests if needed.

## Adding a New Strategy
1. Create a new module in `services/opportunity_engine/` (e.g., `my_strategy.py`).
2. Subscribe to `quotes` or `balances` topics as needed.
3. Emit `Opportunity` objects to the `opportunities` topic.
4. Add tests in `tests/` to validate logic.

## Adding a New Risk Control
1. Implement a new risk module in `services/risk_manager/`.
2. Subscribe to `opportunities`, perform checks, and forward valid ones to `approved_opps`.
3. Update documentation and configs.

## Adding Monitoring/Alerting
1. Add new Prometheus metrics in `services/monitor_service/metrics.py`.
2. Update Grafana dashboards and Alertmanager rules.

## Other Extensibility
- All services use event-driven messaging (Kafka/Redis), so new consumers/producers can be added without code changes to others.
- Use Pydantic models in `common/models.py` for all new message types.
- Update `infra/` for deployment scripts and manifests as needed.
