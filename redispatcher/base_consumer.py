from __future__ import annotations

from abc import ABC, abstractmethod

from aioredis import Redis
from pydantic import BaseModel

from redispatcher.exceptions import UndefinedMessage, UndefinedQueue
from redispatcher.types import MessageContainer


class BaseConsumer(ABC):

    QUEUE: str
    redis_client: Redis

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if not hasattr(cls, "QUEUE") or not cls.QUEUE:
            raise UndefinedQueue(f"{cls.__name__} must define a queue name")

        if not cls.Message.schema().get("properties"):
            raise UndefinedMessage(f"{cls.__name__} must define a Message")

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    @classmethod
    async def dispatch(cls, message_body: BaseModel, redis_client: Redis):
        headers = cls.headers()
        message = MessageContainer(body=message_body.dict(), headers=headers.dict())
        return await redis_client.rpush(cls.QUEUE, message.json())

    def __repr__(self) -> str:
        return f"<redispatcher Consumer: {self.QUEUE}>"

    """
    User-definable methods and properties below
    """

    class Headers(BaseModel):
        """
        Headers are optional. If you want to use them, you must define their shape here. Headers
        are created at dispatch time and are useful for storing metadata such as for tracing.
        """

    class Message(BaseModel):
        """
        This will define the shape of the message that will be passed to your consumer. All messages
        will by validated by Pydantic to ensure they match the correct shape and types.
        """

    @abstractmethod
    async def process_message(self, message: Message, headers: Headers):
        """
        This method is called by the redispatcher consumer loop, and it is the main entrypoint for
        your consumer. Override this method in your consumer with your business logic.
        """
        raise NotImplementedError

    @classmethod
    def headers(cls) -> Headers:
        """
        Headers are optional. If you want to use them, you must override this function to return a
        cls.Headers object here with the shape and types defined above. Headers are created at dispatch
        time and are useful for storing metadata such as for tracing.
        """
        return cls.Headers()
