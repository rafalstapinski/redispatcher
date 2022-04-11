import os
from threading import Event, Thread
from time import sleep

from aioredis import RedisConnection
from redis.client import Redis

from redispatcher import ConsumerConfig, Redispatcher, RedispatcherConfig

from test.fixtures.consumers import ConsumerOne


def test_connect_with_url(redis: Redis):

    config = RedispatcherConfig(
        consumers=[ConsumerConfig(consumer_class=ConsumerOne)], redis_dsn="redis://localhost:1234/0", exit_event=Event()
    )
    dispatcher = Redispatcher(config)

    thread = Thread(target=dispatcher.start)
    thread.start()
    sleep(0.01)

    connection: RedisConnection = dispatcher.redis_client.connection
    assert connection.closed == False

    config.exit_event.set()
    thread.join()


def test_connect_with_environ(redis: Redis):

    os.environ["REDIS_DSN"] = "redis://localhost:1234/0"
    config = RedispatcherConfig(consumers=[ConsumerConfig(consumer_class=ConsumerOne)], exit_event=Event())
    dispatcher = Redispatcher(config)

    thread = Thread(target=dispatcher.start)
    thread.start()
    sleep(0.001)

    connection: RedisConnection = dispatcher.redis_client.connection
    assert connection.closed == False

    config.exit_event.set()
    thread.join()
