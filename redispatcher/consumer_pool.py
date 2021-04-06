import asyncio
import json
from typing import List, Type

import aioredis
from pydantic import BaseModel, BaseSettings, RedisDsn

from redispatcher.base_consumer import BaseConsumer
from redispatcher.config import ConsumerConfig, RedispatcherConfig
from redispatcher.models import MessageContainer


class ConsumerPool:
    def __init__(self, config: RedispatcherConfig):

        self.config = config
        self.loop = asyncio.get_event_loop()

        # this will act as our pool of available workers
        self.pool = asyncio.Queue()
        for consumer_config in config.consumers:
            # toss them all on to the queue
            self.pool.put_nowait(consumer_config.consumer_class())

    async def _consume_wrapper(self, consumer: BaseConsumer, message_str: str):
        # this will run the worker on our message
        # once done, we add our worker back to our pool of ready workers

        try:
            message_body = consumer.Message(**json.loads(message_str)["body"])
            message_headers = consumer.Headers(**json.loads(message_str)["headers"])

            await consumer.process_message(message_body, message_headers)
        except Exception:
            ...
        finally:
            await self.pool.put(consumer)

    async def _run(self):

        self.redis_client = await aioredis.create_redis_pool(self.config.redis_dsn)

        # we go through our consumers round robin (ish) style, getting the first
        # available one, processing it in the background, and adding it back to the
        # pool at the end of the queue

        while True:
            # block until we get a free worker from our pool
            consumer: BaseConsumer = await self.pool.get()

            await asyncio.sleep(1)

            # for this worker, try to get a message
            message = await self.redis_client.lpop(consumer.QUEUE)

            # if there is a message for this worker, lets consume it
            if message:
                # we use ensure_future to run this bit of work in the background so we
                # can move on to listening for messages from the next available worker
                asyncio.ensure_future(self._consume_wrapper(consumer, message))

            else:
                await self.pool.put(consumer)

    def start(self):
        self.loop.run_until_complete(self._run())
