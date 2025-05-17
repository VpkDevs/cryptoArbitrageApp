"""Asynchronous market data collector using ccxtpro websockets."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List

import ccxt.pro as ccxtpro

from common.config import load_config
from common.models import Quote
from common.messaging import JsonKafkaProducer

logger = logging.getLogger(__name__)


class MarketDataCollector:
    def __init__(self, symbols: List[str]) -> None:
        self.cfg = load_config()
        self.symbols = symbols
        self.exchanges: Dict[str, Any] = {}
        self.producer: JsonKafkaProducer | None = None

    async def _init_exchanges(self) -> None:
        for exch_name, creds in self.cfg.exchanges.items():
            try:
                ex = getattr(ccxtpro, exch_name)({
                    "apiKey": creds.api_key,
                    "secret": creds.secret,
                    "password": creds.password,
                    "enableRateLimit": True,
                })
                await ex.load_markets()
                self.exchanges[exch_name] = ex
                logger.info("Initialized exchange %s", exch_name)
            except Exception as exc:  # pragma: no cover
                logger.exception("Error initializing exchange %s: %s", exch_name, exc)

    async def _collect_from_exchange(self, name: str, exchange: Any) -> None:  # type: ignore[override]
        while True:
            try:
                for symbol in self.symbols:
                    ticker = await exchange.watch_ticker(symbol)
                    quote = Quote(
                        exchange=name,
                        symbol=symbol,
                        bid=float(ticker["bid"] or 0),
                        ask=float(ticker["ask"] or 0),
                    )
                    await self.producer.send(quote.dict())  # type: ignore[arg-type]
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # pragma: no cover
                logger.exception("Error collecting data from %s: %s", name, exc)
                await asyncio.sleep(5)

    async def run(self) -> None:
        await self._init_exchanges()
        self.producer = JsonKafkaProducer(
            topic="quotes",
            bootstrap_servers=self.cfg.kafka.bootstrap_servers,
        )
        await self.producer.start()

        tasks = [asyncio.create_task(self._collect_from_exchange(n, e)) for n, e in self.exchanges.items()]
        await asyncio.gather(*tasks)

    async def close(self) -> None:
        if self.producer:
            await self.producer.stop()
        for ex in self.exchanges.values():
            await ex.close()


def main() -> None:
    import uvloop

    uvloop.install()
    symbols = ["BTC/USDT", "ETH/USDT"]
    collector = MarketDataCollector(symbols=symbols)

    try:
        asyncio.run(collector.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(collector.close())


if __name__ == "__main__":
    main()
