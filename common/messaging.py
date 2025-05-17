"""Kafka/Redis messaging wrappers."""
from __future__ import annotations

import json
import logging
from asyncio import Queue
from typing import Any, AsyncIterator, Dict

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logger = logging.getLogger(__name__)


class JsonKafkaProducer:
    def __init__(self, topic: str, **kafka_kwargs: Any) -> None:
        self._producer = AIOKafkaProducer(value_serializer=lambda x: json.dumps(x).encode(), **kafka_kwargs)
        self._topic = topic

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def send(self, msg: Dict[str, Any]) -> None:
        await self._producer.send_and_wait(self._topic, msg)


class JsonKafkaConsumer:
    def __init__(self, topic: str, group_id: str, **kafka_kwargs: Any) -> None:
        self._consumer = AIOKafkaConsumer(
            topic,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode()),
            **kafka_kwargs,
        )
        self._queue: Queue[Dict[str, Any]] = Queue()

    async def start(self) -> None:
        await self._consumer.start()

    async def stop(self) -> None:
        await self._consumer.stop()

    async def _consume(self) -> None:
        async for msg in self._consumer:
            await self._queue.put(msg.value)

    async def messages(self) -> AsyncIterator[Dict[str, Any]]:
        while True:
            yield await self._queue.get()
