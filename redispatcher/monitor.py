import argparse
import asyncio
import curses
import importlib
from typing import Dict, List

import aioredis
from pydantic import BaseModel

from redispatcher.config import RedispatcherConfig
from redispatcher.exceptions import InvalidConfig

TITLE = "Monitoring Redispatcher on {redis_dsn}"
BOTTOM_BAR = "Press 'q' to exit monitoring"


class Metric(BaseModel):
    queue: str
    depths: List[int]


class ColorPairs:
    TITLE = 1
    MAIN = 2
    BOTTOM_BAR = 3


def draw(screen: curses.window, redis_dsn: str, metrics: List[Metric]):

    key = screen.getch()

    if key == ord("q"):
        return True

    screen = curses.initscr()

    curses.cbreak()

    screen.clear()

    curses.start_color()
    curses.init_pair(ColorPairs.TITLE, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(ColorPairs.MAIN, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(ColorPairs.BOTTOM_BAR, curses.COLOR_BLACK, curses.COLOR_WHITE)

    height, width = screen.getmaxyx()

    screen.move(height - 1, width - 1)

    title = TITLE.format(redis_dsn=redis_dsn)

    screen.attron(curses.color_pair(ColorPairs.TITLE))
    screen.addstr(2, int((width - len(title)) / 2), title)
    screen.attroff(curses.color_pair(ColorPairs.TITLE))
    y_offset = 10

    for i, metric in enumerate(metrics):
        screen.attron(curses.color_pair(ColorPairs.MAIN))
        screen.addstr(y_offset + i, 5, f"{metric.queue}: {' '.join(metric.depths)}")
        screen.attroff(curses.color_pair(ColorPairs.MAIN))

    screen.attron(curses.color_pair(ColorPairs.BOTTOM_BAR))

    screen.addstr(height - 1, 0, BOTTOM_BAR)
    screen.addstr(height - 1, len(BOTTOM_BAR), " " * (width - len(BOTTOM_BAR) - 1))
    screen.attroff(curses.color_pair(ColorPairs.BOTTOM_BAR))
    screen.refresh()


async def _cli_configs_stats(config: RedispatcherConfig):

    screen = curses.initscr()
    screen.nodelay(True)
    redis: aioredis.Redis = await aioredis.create_redis(config.redis_dsn)

    metrics: Dict[str, Metric] = {}

    for consumer_config in config.consumers:

        print(consumer_config)

        consumer_class = consumer_config.consumer_class
        metrics[consumer_class.QUEUE] = Metric(queue=consumer_class.QUEUE, depths=[])

    while True:

        await asyncio.sleep(1)

        for consumer_config in config.consumers:
            consumer_class = consumer_config.consumer_class
            queue_size = await redis.llen(consumer_class.QUEUE)
            metric = metrics[consumer_class.QUEUE]

            if len(metric.depths) > 10:
                metric.depths.pop(-1)

            metrics[consumer_class.QUEUE].depths.insert(0, str(queue_size))

        metrics_list = sorted(metrics.values(), key=lambda m: m.queue)

        done = draw(screen, str(config.redis_dsn), metrics_list)

        if done:
            screen.clear()
            screen.refresh()
            break


def monitor_cli():

    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="path to the worker pool config (my.module.path:config)")
    args = parser.parse_args()

    config_path: str = args.config_path
    config_path = config_path.replace("/", ".").replace(".py", "")
    module_path, config_name = config_path.split(":")

    module = importlib.import_module(module_path)

    config = getattr(module, config_name)

    if not isinstance(config, RedispatcherConfig):
        raise InvalidConfig(f"{config_name} is not a valid RedispatcherConfig")

    asyncio.run(_cli_configs_stats(config))
