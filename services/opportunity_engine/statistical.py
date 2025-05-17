"""Statistical arbitrage detector (spread/cointegration demo)."""
from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Deque, Dict, List

from common.config import load_config
from common.messaging import JsonKafkaConsumer, JsonKafkaProducer
from common.models import Opportunity, OrderIntent, Quote, Side

logger = logging.getLogger(__name__)

class StatisticalArbDetector:
    WINDOW = 100
    THRESH = 1.5  # z-score

    def __init__(self, symbol_a: str, symbol_b: str) -> None:
        self.cfg = load_config()
        self.symbol_a = symbol_a
        self.symbol_b = symbol_b
        self.history_a: Deque[float] = deque(maxlen=self.WINDOW)
        self.history_b: Deque[float] = deque(maxlen=self.WINDOW)
        self.producer: JsonKafkaProducer | None = None
        self.consumer: JsonKafkaConsumer | None = None

    def _zscore(self) -> float:
        if len(self.history_a) < self.WINDOW or len(self.history_b) < self.WINDOW:
            return 0.0
        import numpy as np
        spread = np.array(self.history_a) - np.array(self.history_b)
        return float((spread[-1] - spread.mean()) / (spread.std() + 1e-9))

    async def _process_quote(self, quote: Quote) -> None:
        if quote.symbol == self.symbol_a:
            self.history_a.append(quote.bid)
        elif quote.symbol == self.symbol_b:
            self.history_b.append(quote.bid)
        z = self._zscore()
        if abs(z) > self.THRESH:
            # Opportunity: mean reversion
            opp = Opportunity(
                type="statistical",
                symbol=f"{self.symbol_a}-{self.symbol_b}",
                est_profit_pct=abs(z),
                est_profit_abs=abs(z),
                risk_score=1.5,
                legs=[
                    OrderIntent(
                        exchange=quote.exchange,
                        symbol=self.symbol_a,
                        side=Side.SELL if z > 0 else Side.BUY,
                        price=quote.bid,
                        size=0.01,
                        strategy="stat_arb",
                    ),
                    OrderIntent(
                        exchange=quote.exchange,
                        symbol=self.symbol_b,
                        side=Side.BUY if z > 0 else Side.SELL,
                        price=quote.bid,
                        size=0.01,
                        strategy="stat_arb",
                    ),
                ],
            )
            await self.producer.send(opp.dict())
            logger.info("Statistical arb z=%.2f on %s/%s", z, self.symbol_a, self.symbol_b)

    async def run(self) -> None:
        self.consumer = JsonKafkaConsumer(
            topic="quotes",
            group_id="stat-arb",
            bootstrap_servers=self.cfg.kafka.bootstrap_servers,
        )
        await self.consumer.start()
        self.producer = JsonKafkaProducer(
            topic="opportunities",
            bootstrap_servers=self.cfg.kafka.bootstrap_servers,
        )
        await self.producer.start()
        async for msg in self.consumer.messages():
            quote = Quote(**msg)
            await self._process_quote(quote)

    async def close(self) -> None:
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

def main() -> None:
    import uvloop
    uvloop.install()
    detector = StatisticalArbDetector("BTC/USDT", "ETH/USDT")
    try:
        asyncio.run(detector.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(detector.close())

if __name__ == "__main__":
    main()
