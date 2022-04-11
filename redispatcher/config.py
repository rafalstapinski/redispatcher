from optparse import Option
from threading import Event
from typing import List, Optional, Type, Union

from pydantic import BaseModel, BaseSettings, RedisDsn

from redispatcher.base_consumer import BaseConsumer
from redispatcher.types import Logger


class ConsumerConfig(BaseModel):
    consumer_class: Type[BaseConsumer]


class RedispatcherConfig(BaseSettings):
    consumers: List[ConsumerConfig]
    logger: Optional[Logger] = None
    redis_dsn: Optional[Union[RedisDsn, str]] = None
    exit_event: Optional[Event] = None
