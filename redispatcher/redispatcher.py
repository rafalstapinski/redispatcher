import asyncio
import logging

import aioredis
from aioredis import Redis

from redispatcher.base_consumer import BaseConsumer
from redispatcher.config import RedispatcherConfig
from redispatcher.types import MessageContainer


class Redispatcher:

    redis_client: Redis

    def __init__(self, config: RedispatcherConfig):

        self.config = config
        self.logger = self.config.logger or logging.getLogger(__name__)

        self.consumer_pool = asyncio.Queue()

    async def _consume(self, consumer: BaseConsumer, message_str: str):

        # Parse
        try:
            message = MessageContainer.parse_raw(message_str)
            message_body = consumer.Message.parse_obj(message.body)
            message_headers = consumer.Headers.parse_obj(message.headers)
        except Exception as e:
            self.logger.exception(f"Error parsing message {consumer.QUEUE=} {message_str=} {e=}")

        # Process
        try:
            await consumer.process_message(message_body, message_headers)
        except Exception as e:
            ...

    async def _run(self):

        self.logger.info("Starting redispatcher")

        self.redis_client = await aioredis.create_redis(self.config.redis_dsn)

        # Toss consumers on the queue
        for consumer_config in self.config.consumers:
            consumer = consumer_config.consumer_class(self.redis_client)

            self.logger.info(f"Initializing {consumer}")
            await self.consumer_pool.put(consumer)

        self.logger.info("Starting to listen for messages")

        # Go through our consumers round robin (ish) style, getting the first
        # available one, processing it in the background if there is a message,
        # and adding it back to the pool
        while True:

            # Check for configured exit event. Tbh mostly used for testing
            if self.config.exit_event and self.config.exit_event.is_set():
                self.logger.info(f"Got exit event, exiting")
                return

            # Wait for next available consumer
            # print(self.consumer_pool.qsize())
            consumer: BaseConsumer = await self.consumer_pool.get()

            # Get a message
            message = await self.redis_client.lpop(consumer.QUEUE)

            # Let's consume it
            if message:
                # We use ensure_future to run this bit of work in the background so we
                # can move on to listening for messages from the next available worker
                asyncio.ensure_future(self._consume(consumer, message))

            await self.consumer_pool.put(consumer)

    def start(self):
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            self.logger.info("Received KeyboardInterrupt... shutting down")
        except Exception as e:
            self.logger.exception(f"Closing redispatcher {e=}")
