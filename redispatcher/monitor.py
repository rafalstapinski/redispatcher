import argparse
import asyncio
import importlib
from typing import List

import aioredis

from .base_consumer import BaseConsumer
from .config import RedispatcherConfig


async def _cli_configs_stats(configs: List[RedispatcherConfig]):

    config = configs[0]

    for config in configs:
        redis: aioredis.Redis = await aioredis.create_redis(config.redis_dsn)

        metrics: List[str, int] = []

        for consumer_config in config.consumers:
            consumer_class = consumer_config.consumer_class
            queue_size = await redis.llen(consumer_class.QUEUE)
            metrics.append((consumer_class.QUEUE, queue_size))

        metrics = sorted(metrics, key=lambda q: q[0])
        print(f"Redis: {config.redis_dsn}")
        print("Queues:")
        for metric in metrics:
            print(f" - {metric[0]}\t - \t {metric[1]}")
        print("\n")


def monitor_cli():

    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="path to the worker pool config (my.module.path:config)")
    args = parser.parse_args()

    mod = importlib.import_module(args.config_path)

    configs_to_process = []

    for thing_name in dir(mod):
        thing = getattr(mod, thing_name)

        if isinstance(thing, RedispatcherConfig):
            configs_to_process.append(thing)

    asyncio.run(_cli_configs_stats(configs_to_process))
