"""FastAPI gateway for monitoring and overrides."""
from __future__ import annotations

import asyncio
from typing import List

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio

from common.config import load_config
from common.messaging import JsonKafkaConsumer
from common.models import Opportunity, Balance

app = FastAPI(title="Crypto Arb Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cfg = load_config()

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/opportunities", response_model=List[Opportunity])
async def get_recent_opps() -> List[Opportunity]:
    consumer = JsonKafkaConsumer(
        topic="opportunities",
        group_id="api-gateway-snapshot",
        bootstrap_servers=cfg.kafka.bootstrap_servers,
    )
    await consumer.start()
    opps: List[Opportunity] = []
    try:
        for _ in range(100):
            try:
                msg = await asyncio.wait_for(consumer._queue.get(), timeout=0.1)
                opps.append(Opportunity(**msg))
            except asyncio.TimeoutError:
                break
    finally:
        await consumer.stop()
    return opps

@app.get("/balances", response_model=List[Balance])
async def get_recent_balances() -> List[Balance]:
    consumer = JsonKafkaConsumer(
        topic="balances",
        group_id="api-gateway-balances",
        bootstrap_servers=cfg.kafka.bootstrap_servers,
    )
    await consumer.start()
    bals: List[Balance] = []
    try:
        for _ in range(100):
            try:
                msg = await asyncio.wait_for(consumer._queue.get(), timeout=0.1)
                bals.append(Balance(**msg))
            except asyncio.TimeoutError:
                break
    finally:
        await consumer.stop()
    return bals

@app.get("/audit")
async def get_audit_log() -> List[dict]:
    # Placeholder: return sample audit log
    return [
        {"timestamp": "2025-04-18T20:00:00Z", "event": "startup", "details": "System started"},
        {"timestamp": "2025-04-18T20:10:00Z", "event": "trade", "details": "Executed BTC/USDT arbitrage"},
    ]

@app.post("/override/kill")
async def kill_switch():
    # Placeholder: implement authenticated kill switch logic
    # In production, use secure authentication and trigger kill event
    return JSONResponse({"status": "kill switch triggered"})

@app.websocket("/ws/opportunities")
async def ws_opps(ws: WebSocket) -> None:
    await ws.accept()
    consumer = JsonKafkaConsumer(
        topic="opportunities",
        group_id="api-gateway-ws",
        bootstrap_servers=cfg.kafka.bootstrap_servers,
    )
    await consumer.start()
    try:
        async for msg in consumer.messages():
            await ws.send_json(msg)
    finally:
        await consumer.stop()
