"""Triangular arbitrage detector (within-exchange loops)."""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Dict, List

from common.config import load_config
from common.messaging import JsonKafkaConsumer, JsonKafkaProducer
from common.models import Opportunity, OrderIntent, Quote, Side

logger = logging.getLogger(__name__)

class TriangularArbDetector:
    def __init__(self, symbols: List[str]) -> None:
        self.cfg = load_config()
        self.symbols = symbols
        self.exchange_quotes: Dict[str, Dict[str, Quote]] = defaultdict(dict)
        self.producer: JsonKafkaProducer | None = None
        self.consumer: JsonKafkaConsumer | None = None

    async def _process_quote(self, quote: Quote) -> None:
        self.exchange_quotes[quote.exchange][quote.symbol] = quote
        # For demo: look for BTC/ETH, ETH/USDT, BTC/USDT triangle
        syms = {"BTC/ETH", "ETH/USDT", "BTC/USDT"}
        if not syms.issubset(self.exchange_quotes[quote.exchange]):
            return
        q1 = self.exchange_quotes[quote.exchange]["BTC/ETH"]
        q2 = self.exchange_quotes[quote.exchange]["ETH/USDT"]
        q3 = self.exchange_quotes[quote.exchange]["BTC/USDT"]
        # Compute implied rates
        implied = q1.bid * q2.bid
        direct = q3.ask
        spread = (implied - direct) / direct * 100
        if spread > 0.15:
            opp = Opportunity(
                type="triangular",
                symbol="BTC/ETH/USDT",
                est_profit_pct=spread,
                est_profit_abs=(implied - direct),
                risk_score=1.2,
                legs=[
                    OrderIntent(
                        exchange=quote.exchange,
                        symbol="BTC/ETH",
                        side=Side.SELL,
                        price=q1.bid,
                        size=0.01,
                        strategy="tri_sell1",
                    ),
                    OrderIntent(
                        exchange=quote.exchange,
                        symbol="ETH/USDT",
                        side=Side.SELL,
                        price=q2.bid,
                        size=0.01,
                        strategy="tri_sell2",
                    ),
                    OrderIntent(
                        exchange=quote.exchange,
                        symbol="BTC/USDT",
                        side=Side.BUY,
                        price=q3.ask,
                        size=0.01,
                        strategy="tri_buy3",
                    ),
                ],
            )
            await self.producer.send(opp.dict())
            logger.info("Triangular opportunity %.3f%% on %s", spread, quote.exchange)

    async def run(self) -> None:
        self.consumer = JsonKafkaConsumer(
            topic="quotes",
            group_id="tri-arb",
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
    detector = TriangularArbDetector(["BTC/ETH", "ETH/USDT", "BTC/USDT"])
    try:
        asyncio.run(detector.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(detector.close())

if __name__ == "__main__":
    main()
