"""Pydantic models shared across services."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class Quote(BaseModel):
    exchange: str
    symbol: str
    bid: float
    ask: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OrderIntent(BaseModel):
    exchange: str
    symbol: str
    side: Side
    price: float
    size: float
    strategy: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrderStatus(str, Enum):
    NEW = "new"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELED = "canceled"
    ERROR = "error"


class Order(BaseModel):
    id: str
    intent: OrderIntent
    status: OrderStatus
    filled_size: float = 0.0
    avg_price: Optional[float] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Balance(BaseModel):
    exchange: str
    asset: str
    total: float
    available: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Opportunity(BaseModel):
    type: str  # spatial, tri, etc.
    symbol: str
    legs: List[OrderIntent]
    est_profit_pct: float
    est_profit_abs: float
    risk_score: float
    detected_at: datetime = Field(default_factory=datetime.utcnow)
