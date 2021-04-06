from typing import List, Type

from pydantic import BaseModel, BaseSettings, RedisDsn

from redispatcher.base_consumer import BaseConsumer


class ConsumerConfig(BaseModel):
    consumer_class: Type[BaseConsumer]


class RedispatcherConfig(BaseSettings):
    consumers: List[ConsumerConfig]
    redis_dsn: RedisDsn
