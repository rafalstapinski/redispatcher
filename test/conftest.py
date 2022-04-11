import shutil
from threading import Event, Thread
from time import sleep

import pytest
from pytest_redis import factories

from redispatcher import ConsumerConfig, Redispatcher, RedispatcherConfig

from test.fixtures.consumers import ConsumerOne, ConsumerTwo

redis_proc = factories.redis_proc(executable=shutil.which("redis-server"), port=1234)
redis = factories.redisdb("redis_proc")


@pytest.fixture
def dispatcher():

    config = RedispatcherConfig(
        redis_dsn="redis://localhost:1234/0",
        exit_event=Event(),
        consumers=[ConsumerConfig(consumer_class=ConsumerOne), ConsumerConfig(consumer_class=ConsumerTwo)],
    )

    dispatcher = Redispatcher(config)

    thread = Thread(target=dispatcher.start)
    thread.start()
    sleep(0.01)

    yield dispatcher

    config.exit_event.set()
    thread.join()
