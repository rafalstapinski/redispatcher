
from pydantic import BaseModel

from redispatcher import BaseConsumer


class ConsumerOne(BaseConsumer):
    QUEUE = "queue-one"

    class Message(BaseConsumer.Message):
        id: int
        text: str

    async def process_message(self, message: Message, headers: BaseConsumer.Headers): ...


class ConsumerTwo(BaseConsumer):
    QUEUE = "queue-two"

    class Message(BaseModel):
        id: int
        text: str

    class Headers(BaseModel):
        trace_id: str

    @classmethod
    def headers(cls) -> Headers:
        return cls.Headers(trace_id="1234")

    async def process_message(self, message: Message, headers: BaseConsumer.Headers):
        await self.redis_client.set("message1", message.json())
        await self.redis_client.set("headers1", headers.json())
