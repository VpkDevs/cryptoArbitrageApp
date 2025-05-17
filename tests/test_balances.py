import asyncio

import pytest

from services.portfolio_service.balances import BalanceCollector

@pytest.mark.asyncio
async def test_balance_collector(monkeypatch):
    collector = BalanceCollector(assets=["BTC"])
    sent = []
    class DummyProducer:
        async def send(self, msg):
            sent.append(msg)
    collector.producer = DummyProducer()
    class DummyExchange:
        async def fetch_balance(self):
            return {"total": {"BTC": 1.5}, "free": {"BTC": 1.0}}
    collector.exchanges = {"binance": DummyExchange()}
    await collector._collect_one("binance", collector.exchanges["binance"])
    assert sent, "Should send balance message"
