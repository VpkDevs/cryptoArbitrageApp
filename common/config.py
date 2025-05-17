from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl, validator

load_dotenv()


class KafkaSettings(BaseModel):
    bootstrap_servers: str = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")
    security_protocol: str = Field("PLAINTEXT", env="KAFKA_SECURITY_PROTOCOL")
    sasl_mechanism: Optional[str] = Field(None, env="KAFKA_SASL_MECHANISM")
    sasl_username: Optional[str] = Field(None, env="KAFKA_SASL_USERNAME")
    sasl_password: Optional[str] = Field(None, env="KAFKA_SASL_PASSWORD")


class RedisSettings(BaseModel):
    url: str = Field(..., env="REDIS_URL")


class ExchangeCreds(BaseModel):
    api_key: str
    secret: str
    password: Optional[str] = None


class AppConfig(BaseModel):
    environment: str = Field("dev", env="ENVIRONMENT")
    kafka: KafkaSettings
    redis: RedisSettings
    exchanges: Dict[str, ExchangeCreds]
    log_level: str = Field("INFO", env="LOG_LEVEL")

    @validator("environment")
    def validate_env(cls, v: str) -> str:
        if v not in {"dev", "prod", "test"}:
            raise ValueError("environment must be dev, prod, or test")
        return v


@lru_cache
def load_config(config_path: Optional[str | Path] = None) -> AppConfig:  # type: ignore[type-var]
    """Load configuration from yaml file + env overrides."""
    import yaml

    path = Path(config_path) if config_path else Path(os.getenv("CONFIG_PATH", "config.yaml"))
    if not path.exists():
        raise FileNotFoundError(f"Config file {path} not found")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return AppConfig(**raw)
