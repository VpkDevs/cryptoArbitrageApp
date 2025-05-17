"""Scrapes Kafka lag and custom metrics, exposes Prometheus endpoint."""
from __future__ import annotations

import asyncio
from contextlib import suppress

from prometheus_client import Gauge, start_http_server

kafka_lag_gauge = Gauge("kafka_consumer_group_lag", "Lag per consumer group", ["group"])


async def collect_lag() -> None:  # placeholder
    while True:
        # TODO: query Kafka for lag
        kafka_lag_gauge.labels(group="exec-engine").set(1)
        await asyncio.sleep(5)


def main() -> None:
    start_http_server(9000)
    with suppress(KeyboardInterrupt):
        asyncio.run(collect_lag())


if __name__ == "__main__":
    main()
