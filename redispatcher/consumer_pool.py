import asyncio
import logging

import aioredis

from redispatcher.base_consumer import BaseConsumer
from redispatcher.config import RedispatcherConfig
from redispatcher.types import MessageContainer


class ConsumerPool:
    def __init__(self, config: RedispatcherConfig):

        self.config = config
        self.loop = asyncio.get_event_loop()
        self.logger = self.config.logger or logging.getLogger(__name__)

        self.consumer_pool = asyncio.Queue()

    async def _consume_wrapper(self, consumer: BaseConsumer, message_str: str):
        # this will run the worker on our message
        # once done, we add our worker back to our pool of ready workers

        try:
            message = MessageContainer.parse_raw(message_str)
            message_body = consumer.Message.parse_obj(message.body)
            message_headers = consumer.Headers.parse_obj(message.headers)
            await consumer.process_message(message_body, message_headers)

        except (ValueError, TypeError, UnicodeDecodeError) as e:
            self.logger.exception(f"Error parsing message in {consumer.QUEUE}. {message_str=}", e)
        except Exception:
            ...
        finally:
            await self.consumer_pool.put(consumer)

    async def _run(self):

        self.logger.info("Starting redispatcher")
        self.redis_client = await aioredis.create_redis_pool(self.config.redis_dsn)

        for consumer_config in self.config.consumers:
            # toss them all on to the queue
            consumer = consumer_config.consumer_class()
            self.logger.info(f"Initializing {consumer}")
            self.consumer_pool.put_nowait(consumer)

        self.logger.info("Starting to listen for messages")

        # we go through our consumers round robin (ish) style, getting the first
        # available one, processing it in the background if there is a message,
        # and adding it back to the pool
        while True:
            # block until we get a free worker from our pool
            consumer: BaseConsumer = await self.consumer_pool.get()

            # for this worker, try to get a message
            message = await self.redis_client.lpop(consumer.QUEUE)

            # if there is a message for this worker, lets consume it
            if message:
                # we use ensure_future to run this bit of work in the background so we
                # can move on to listening for messages from the next available worker
                asyncio.ensure_future(self._consume_wrapper(consumer, message))

            else:
                await self.consumer_pool.put(consumer)

    def start(self):
        self.loop.run_until_complete(self._run())
