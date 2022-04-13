from __future__ import annotations

from abc import ABC, abstractmethod

from aioredis import Redis
from pydantic import BaseModel

from redispatcher.exceptions import UndefinedMessage, UndefinedQueue
from redispatcher.types import MessageContainer


class BaseConsumer(ABC):

    QUEUE: str = None
    redis_client: Redis

    class Headers(BaseModel):
        ...

    class Message(BaseModel):
        ...

    def __init_subclass__(cls) -> None:

        if not cls.QUEUE:
            raise UndefinedQueue(f"{cls.__name__} must define a queue name")

        if not cls.Message.schema()["properties"]:
            raise UndefinedMessage(f"{cls.__name__} must define a Message")

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    @classmethod
    async def publish(cls, message_body: BaseModel, redis_client: Redis):
        headers = cls.headers()
        message = MessageContainer(body=message_body.dict(), headers=headers.dict())
        resp = await redis_client.rpush(cls.QUEUE, message.json())

    @classmethod
    def headers(cls) -> Headers:
        return cls.Headers()

    @abstractmethod
    async def process_message(self, message: Message, headers: Headers):
        ...

    def __repr__(self) -> str:
        return f"<redispatcher Consumer: {self.QUEUE}>"
