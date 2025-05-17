"""Basic execution engine with mock order placement for demo."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

import ccxt.async_support as ccxt

from common.config import load_config
from common.messaging import JsonKafkaConsumer
from common.models import Opportunity, OrderIntent

logger = logging.getLogger(__name__)


class BasicExecutionEngine:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.exchanges: Dict[str, Any] = {}
        self.consumer: JsonKafkaConsumer | None = None

    async def _init_exchanges(self) -> None:
        for name, creds in self.cfg.exchanges.items():
            ex = getattr(ccxt, name)({
                "apiKey": creds.api_key,
                "secret": creds.secret,
                "password": creds.password,
                "enableRateLimit": True,
            })
            await ex.load_markets()
            self.exchanges[name] = ex

    async def _exec_intent(self, intent: OrderIntent) -> None:
        ex = self.exchanges[intent.exchange]
        side = intent.side.value
        logger.info("Placing %s %s %s @ %s", intent.exchange, side, intent.symbol, intent.price)
        try:
            order = await ex.create_order(
                symbol=intent.symbol,
                type="limit",
                side=side,
                amount=intent.size,
                price=intent.price,
            )
            logger.info("Order result %s", order)
        except Exception as exc:  # pragma: no cover
            logger.exception("Order error: %s", exc)

    async def _handle_opportunity(self, opp: Opportunity) -> None:
        # naive risk filter
        if opp.est_profit_pct < 0.2:
            return
        tasks = [asyncio.create_task(self._exec_intent(leg)) for leg in opp.legs]
        await asyncio.gather(*tasks)

    async def run(self) -> None:
        await self._init_exchanges()
        self.consumer = JsonKafkaConsumer(
            topic="opportunities",
            group_id="exec-engine",
            bootstrap_servers=self.cfg.kafka.bootstrap_servers,
        )
        await self.consumer.start()

        async for msg in self.consumer.messages():
            opp = Opportunity(**msg)
            await self._handle_opportunity(opp)

    async def close(self) -> None:
        if self.consumer:
            await self.consumer.stop()
        for ex in self.exchanges.values():
            await ex.close()


def main() -> None:
    import uvloop

    uvloop.install()
    engine = BasicExecutionEngine()
    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(engine.close())


if __name__ == "__main__":
    main()
