"""Advanced risk manager with exposure, daily loss, and per‑exchange limits."""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict

from common.config import load_config
from common.messaging import JsonKafkaConsumer, JsonKafkaProducer
from common.models import Opportunity

logger = logging.getLogger(__name__)


class AdvancedRiskManager:
    MAX_NOTIONAL = 1000.0
    DAILY_PNL_LIMIT = -200.0  # stop if PnL drops below
    MAX_EXPOSURE_PER_EXCHANGE = 1500.0

    def __init__(self) -> None:
        self.cfg = load_config()
        self.consumer: JsonKafkaConsumer | None = None
        self.producer: JsonKafkaProducer | None = None
        self.exposure: DefaultDict[str, float] = defaultdict(float)
        self.pnl: float = 0.0
        self.day_start: datetime = datetime.utcnow()

    def _reset_daily(self) -> None:
        if datetime.utcnow() - self.day_start > timedelta(days=1):
            self.pnl = 0.0
            self.day_start = datetime.utcnow()
            logger.info("Daily PnL reset")

    async def _check(self, opp: Opportunity) -> bool:
        self._reset_daily()
        if self.pnl < self.DAILY_PNL_LIMIT:
            logger.warning("Daily loss limit breached")
            return False
        notional = sum(leg.price * leg.size for leg in opp.legs)
        if notional > self.MAX_NOTIONAL:
            return False
        for leg in opp.legs:
            new_exposure = self.exposure[leg.exchange] + leg.price * leg.size
            if new_exposure > self.MAX_EXPOSURE_PER_EXCHANGE:
                return False
        return True

    async def _update_exposure(self, opp: Opportunity) -> None:
        for leg in opp.legs:
            self.exposure[leg.exchange] += leg.price * leg.size

    async def run(self) -> None:
        self.consumer = JsonKafkaConsumer(
            topic="opportunities",
            group_id="adv-risk-manager",
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
            if await self._check(opp):
                await self._update_exposure(opp)
                await self.producer.send(opp.dict())  # type: ignore[arg-type]
            else:
                logger.warning("Advanced risk rejected %s", opp.symbol)

    async def close(self) -> None:
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()


def main() -> None:
    import uvloop

    uvloop.install()
    rm = AdvancedRiskManager()
    try:
        asyncio.run(rm.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(rm.close())


if __name__ == "__main__":
    main()
