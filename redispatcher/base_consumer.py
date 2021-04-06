from __future__ import annotations

import json

import aioredis
from pydantic import BaseModel

from redispatcher.models import MessageContainer


class BaseConsumer:

    QUEUE: str = None
    redis: aioredis.Redis = None

    class Headers(BaseModel):
        ...

    class Message(BaseModel):
        ...

    def __init__(self):
        if not self.QUEUE:
            raise Exception("Queue must be defined")

    @classmethod
    async def publish(cls, message_body: Message, redis_client: aioredis.Redis):
        headers = cls.headers()
        message = MessageContainer(headers=headers, body=message_body)
        await redis_client.rpush(cls.QUEUE, json.dumps(message.dict()))

    @classmethod
    def headers(cls) -> Headers:
        return cls.Headers(**dict())

    async def process_message(self, message: Message, headers: Headers):
        raise NotImplementedError
