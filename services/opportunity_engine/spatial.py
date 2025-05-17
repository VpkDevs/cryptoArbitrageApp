"""Spatial arbitrage detector."""
from __future__ import annotations

import asyncio
import logging
from typing import Dict, List

from common.config import load_config
from common.messaging import JsonKafkaConsumer, JsonKafkaProducer
from common.models import Opportunity, OrderIntent, Quote, Side

logger = logging.getLogger(__name__)


class SpatialArbDetector:
    def __init__(self, symbols: List[str]) -> None:
        self.cfg = load_config()
        self.symbols = symbols
        self.best_bids: Dict[str, Quote] = {}
        self.best_asks: Dict[str, Quote] = {}
        self.producer: JsonKafkaProducer | None = None
        self.consumer: JsonKafkaConsumer | None = None

    async def _process_quote(self, quote: Quote) -> None:
        key = f"{quote.exchange}:{quote.symbol}"
        # update best bid/ask per symbol globally
        if quote.bid:
            current_bid = self.best_bids.get(quote.symbol)
            if not current_bid or quote.bid > current_bid.bid:
                self.best_bids[quote.symbol] = quote
        if quote.ask:
            current_ask = self.best_asks.get(quote.symbol)
            if not current_ask or quote.ask < current_ask.ask:
                self.best_asks[quote.symbol] = quote

        # once we have both, compute spread
        if quote.symbol in self.best_bids and quote.symbol in self.best_asks:
            best_bid = self.best_bids[quote.symbol]
            best_ask = self.best_asks[quote.symbol]
            if best_bid.bid <= 0 or best_ask.ask <= 0:
                return
            spread_pct = (best_bid.bid - best_ask.ask) / best_ask.ask * 100
            if spread_pct > 0.2:  # configurable threshold
                opp = Opportunity(
                    type="spatial",
                    symbol=quote.symbol,
                    est_profit_pct=spread_pct,
                    est_profit_abs=(best_bid.bid - best_ask.ask),
                    risk_score=1.0,  # TODO risk model
                    legs=[
                        OrderIntent(
                            exchange=best_ask.exchange,
                            symbol=quote.symbol,
                            side=Side.BUY,
                            price=best_ask.ask,
                            size=0.01,  # TODO size logic
                            strategy="spatial_buy",
                        ),
                        OrderIntent(
                            exchange=best_bid.exchange,
                            symbol=quote.symbol,
                            side=Side.SELL,
                            price=best_bid.bid,
                            size=0.01,
                            strategy="spatial_sell",
                        ),
                    ],
                )
                await self.producer.send(opp.dict())  # type: ignore[arg-type]
                logger.info(
                    "Spatial opportunity %s %.3f%% %s->%s",
                    quote.symbol,
                    spread_pct,
                    best_ask.exchange,
                    best_bid.exchange,
                )

    async def run(self) -> None:
        self.consumer = JsonKafkaConsumer(
            topic="quotes",
            group_id="spatial-arb",
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
    symbols = ["BTC/USDT", "ETH/USDT"]
    detector = SpatialArbDetector(symbols)
    try:
        asyncio.run(detector.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(detector.close())


if __name__ == "__main__":
    main()
