import logging
import os
from logging import Logger
from threading import Event
from typing import Type

from pydantic import BaseModel, RedisDsn

from redispatcher.base_consumer import BaseConsumer


class ConsumerConfig(BaseModel):
    consumer_class: Type[BaseConsumer]
    count: int = 1


class RedispatcherConfig(BaseModel):
    consumers: list[ConsumerConfig]
    logger: Logger = logging.getLogger("redispatcher")
    redis_dsn: RedisDsn | str = os.environ["REDIS_DSN"]
    exit_event: Event = Event()
