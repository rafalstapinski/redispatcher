import json
from asyncio import sleep
from threading import Event, Thread

import aioredis
import pytest
from redis import Redis
from redis.client import Redis

from redispatcher import ConsumerConfig, Redispatcher, RedispatcherConfig

from test.fixtures.consumers import ConsumerOne, ConsumerTwo


@pytest.mark.asyncio
async def test_publish_and_consume(redis: Redis):

    config = RedispatcherConfig(
        consumers=[ConsumerConfig(consumer_class=ConsumerOne), ConsumerConfig(consumer_class=ConsumerTwo)],
        redis_dsn="redis://localhost:1234/0",
        exit_event=Event(),
    )
    dispatcher = Redispatcher(config)

    thread = Thread(target=dispatcher.start)
    thread.start()
    await sleep(0.01)

    redis_client = await aioredis.create_redis(config.redis_dsn)
    await ConsumerTwo.publish(ConsumerTwo.Message(id=123, text="hello"), redis_client)

    await sleep(0.01)

    assert json.loads(redis.get("message1")) == ConsumerTwo.Message(id=123, text="hello").dict()
    assert json.loads(redis.get("headers1")) == ConsumerTwo.headers().dict()

    config.exit_event.set()
    thread.join()
