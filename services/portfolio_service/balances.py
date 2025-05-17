"""Real‑time balance collector and broadcaster."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

import ccxt.async_support as ccxt

from common.config import load_config
from common.messaging import JsonKafkaProducer
from common.models import Balance

logger = logging.getLogger(__name__)


class BalanceCollector:
    INTERVAL_SEC = 10

    def __init__(self, assets: List[str] | None = None) -> None:
        self.cfg = load_config()
        self.assets = assets or []
        self.exchanges: Dict[str, Any] = {}
        self.producer: JsonKafkaProducer | None = None

    async def _init_exchanges(self) -> None:
        for name, creds in self.cfg.exchanges.items():
            ex = getattr(ccxt, name)({
                "apiKey": creds.api_key,
                "secret": creds.secret,
                "password": creds.password,
                "enableRateLimit": True,
            })
            self.exchanges[name] = ex
            logger.info("BalanceCollector: init %s", name)

    async def _collect_one(self, name: str, ex: Any) -> None:  # type: ignore[override]
        try:
            raw = await ex.fetch_balance()
            for asset, data in raw["total"].items():
                if self.assets and asset not in self.assets:
                    continue
                bal = Balance(
                    exchange=name,
                    asset=asset,
                    total=float(data or 0),
                    available=float(raw["free"].get(asset, 0)),
                )
                await self.producer.send(bal.dict())  # type: ignore[arg-type]
        except Exception as exc:  # pragma: no cover
            logger.exception("Balance fetch error %s: %s", name, exc)

    async def _loop(self) -> None:
        while True:
            tasks = [self._collect_one(n, e) for n, e in self.exchanges.items()]
            await asyncio.gather(*tasks)
            await asyncio.sleep(self.INTERVAL_SEC)

    async def run(self) -> None:
        await self._init_exchanges()
        self.producer = JsonKafkaProducer(
            topic="balances",
            bootstrap_servers=self.cfg.kafka.bootstrap_servers,
        )
        await self.producer.start()
        await self._loop()

    async def close(self) -> None:
        if self.producer:
            await self.producer.stop()
        for ex in self.exchanges.values():
            await ex.close()


def main() -> None:
    import uvloop

    uvloop.install()
    collector = BalanceCollector()
    try:
        asyncio.run(collector.run())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(collector.close())


if __name__ == "__main__":
    main()
