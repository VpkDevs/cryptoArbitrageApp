"""Cross-exchange transfer scheduler and executor."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

import ccxt.async_support as ccxt

from common.config import load_config
from common.messaging import JsonKafkaConsumer
from common.models import Balance

logger = logging.getLogger(__name__)

class TransferScheduler:
    INTERVAL_SEC = 30

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
            self.exchanges[name] = ex
            logger.info("TransferScheduler: init %s", name)

    async def _check_and_transfer(self, bal: Balance) -> None:
        # Placeholder: if available > threshold, transfer to main venue
        THRESH = 0.5
        if bal.available > THRESH:
            logger.info("Would transfer %s %s from %s", bal.available, bal.asset, bal.exchange)
            # TODO: ex.withdraw(...) or ex.transfer(...)

    async def run(self) -> None:
        await self._init_exchanges()
        self.consumer = JsonKafkaConsumer(
            topic="balances",
            group_id="transfer-scheduler",
            bootstrap_servers=self.cfg.kafka.bootstrap_servers,
        )
        await self.consumer.start()
        async for msg in self.consumer.messages():
            bal = Balance(**msg)
            await self._check_and_transfer(bal)

    async def close(self) -> None:
        if self.consumer:
            await self.consumer.stop()
        for ex in self.exchanges.values():
            await ex.close()

def main() -> None:
    import uvloop
    uvloop.install()
    sched = TransferScheduler()
    try:
        asyncio.run(sched.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(sched.close())

if __name__ == "__main__":
    main()
