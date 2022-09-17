import json
from asyncio import sleep
from threading import Event, Thread

import aioredis
import pytest
from redis import Redis

from redispatcher import ConsumerConfig, Redispatcher, RedispatcherConfig

from test.fixtures.consumers import ConsumerOne, ConsumerTwo

config = RedispatcherConfig(
    consumers=[
        ConsumerConfig(
            consumer_class=ConsumerOne,
            count=2,
        ),
        ConsumerConfig(
            consumer_class=ConsumerTwo,
            count=3,
        ),
    ],
    redis_dsn="redis://localhost:1234/0",
    exit_event=Event(),
)


@pytest.mark.asyncio
async def test_publish_and_consume(redis: Redis):

    dispatcher = Redispatcher(config)

    thread = Thread(target=dispatcher.start)
    thread.start()
    await sleep(0.1)

    redis_client = await aioredis.create_redis(config.redis_dsn)
    await ConsumerTwo.dispatch(ConsumerTwo.Message(id=123, text="hello"), redis_client)

    await sleep(0.1)

    assert json.loads(redis.get("message1")) == ConsumerTwo.Message(id=123, text="hello").dict()
    assert json.loads(redis.get("headers1")) == ConsumerTwo.headers().dict()

    config.exit_event.set()
    thread.join()


@pytest.skip
@pytest.mark.asyncio
async def test_consumers_initialized(redis: Redis):
    dispatcher = Redispatcher(config)

    consumers = []
    while not dispatcher.consumer_pool.empty():
        consumers.append(await dispatcher.consumer_pool.get())

    thread = Thread(target=dispatcher.start)
    thread.start()
    await sleep(0.5)

    config.exit_event.set()

    assert len([c for c in consumers if isinstance(c, ConsumerOne)]) == 2
    assert len([c for c in consumers if isinstance(c, ConsumerTwo)]) == 3
