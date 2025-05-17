"""Very simple risk manager that listens to opportunities and rejects if needed."""
from __future__ import annotations

import asyncio
import logging

from common.config import load_config
from common.messaging import JsonKafkaConsumer, JsonKafkaProducer
from common.models import Opportunity

logger = logging.getLogger(__name__)


class BasicRiskManager:
    MAX_TRADE_NOTIONAL = 500.0  # usd

    def __init__(self) -> None:
        self.cfg = load_config()
        self.consumer: JsonKafkaConsumer | None = None
        self.producer: JsonKafkaProducer | None = None

    async def _risk_check(self, opp: Opportunity) -> bool:
        # simplistic check - ensure notional <= MAX_TRADE_NOTIONAL
        for leg in opp.legs:
            if leg.price * leg.size > self.MAX_TRADE_NOTIONAL:
                return False
        return True

    async def run(self) -> None:
        self.consumer = JsonKafkaConsumer(
            topic="opportunities",
            group_id="risk-manager",
            bootstrap_servers=self.cfg.kafka.bootstrap_servers,
        )
        await self.consumer.start()
        self.producer = JsonKafkaProducer(
            topic="approved_opps",
            bootstrap_servers=self.cfg.kafka.bootstrap_servers,
        )
        await self.producer.start()

        async for msg in self.consumer.messages():
            opp = Opportunity(**msg)
            if await self._risk_check(opp):
                await self.producer.send(opp.dict())  # type: ignore[arg-type]
            else:
                logger.warning("Risk rejected opportunity %s", opp.symbol)

    async def close(self) -> None:
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()


def main() -> None:
    import uvloop

    uvloop.install()
    rm = BasicRiskManager()
    try:
        asyncio.run(rm.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(rm.close())


if __name__ == "__main__":
    main()
