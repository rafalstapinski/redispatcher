import logging
import os
from logging import Logger
from threading import Event
from typing import Type

from pydantic import BaseModel, Field, RedisDsn
from pydantic_settings import BaseSettings

from redispatcher.base_consumer import BaseConsumer


class ConsumerConfig(BaseModel):
    consumer_class: Type[BaseConsumer]
    count: int = 1


class RedispatcherConfig(BaseSettings):
    consumers: list[ConsumerConfig]
    logger: Logger = logging.getLogger("redispatcher")
    redis_dsn: RedisDsn = Field("redis://localhost:6379/0")
    exit_event: Event = Event()
