import asyncio

import pytest

from services.opportunity_engine.spatial import SpatialArbDetector


@pytest.mark.asyncio
async def test_spread_calc(monkeypatch):
    detector = SpatialArbDetector(symbols=["BTC/USDT"])

    # monkeypatch producer to capture outputs
    sent = []

    class DummyProducer:
        async def send(self, msg):
            sent.append(msg)

    detector.producer = DummyProducer()

    # craft fake quotes
    from common.models import Quote
    from datetime import datetime

    await detector._process_quote(
        Quote(exchange="A", symbol="BTC/USDT", bid=30000, ask=30010, timestamp=datetime.utcnow())
    )
    await detector._process_quote(
        Quote(exchange="B", symbol="BTC/USDT", bid=30100, ask=30120, timestamp=datetime.utcnow())
    )
    assert sent, "Should emit opportunity when spread > threshold"
