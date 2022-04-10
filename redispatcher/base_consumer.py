from __future__ import annotations

from aioredis import Redis
from pydantic import BaseModel

from redispatcher.exceptions import UndefinedQueue
from redispatcher.types import MessageContainer


class BaseConsumer:

    QUEUE: str = None

    class Headers(BaseModel):
        ...

    class Message(BaseModel):
        ...

    def __init_subclass__(cls) -> None:
        if not cls.QUEUE:
            raise UndefinedQueue(f"{cls.__name__} must define a queue name")

    @classmethod
    async def publish(cls, message_body: Message, redis_client: Redis):
        headers = cls.headers()
        message = MessageContainer(headers=headers, body=message_body)
        await redis_client.rpush(cls.QUEUE, message.json())

    @classmethod
    def headers(cls) -> Headers:
        return cls.Headers()

    async def process_message(self, message: Message, headers: Headers):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<redispatcher Consumer: {self.QUEUE}>"
