# redispatcher

<a href="https://rafalstapinski.github.io/redispatcher">
  <img src="https://rafalstapinski.github.io/redispatcher/img/logo.svg" alt="redispatcher logo" />
</a>

<p align="center">
  <strong>
    <em>
      Utilitarian Python ORM for Postgres, backed by <a href="https://github.com/MagicStack/asyncpg">asyncpg</a>, <a href="https://github.com/samuelcolvin/pydantic">Pydantic</a>, and <a href="https://github.com/kayak/pypika">PyPika</a>
    </em>
  </strong>
</p>

---

**Documentation**: <a href="https://rafalstapinski.github.io/redispatcher">https://rafalstapinski.github.io/redispatcher</a>

**Source Code**: <a href="https://github.com/rafalstapinski/redispatcher">https://github.com/rafalstapinski/redispatcher</a>

---

<p align="center">
  <a href="https://github.com/rafalstapinski/porm/actions/workflows/test.yml" target="_blank">
    <img src="https://github.com/rafalstapinski/porm/actions/workflows/test.yml/badge.svg" alt="Test Status" />
  </a>
  <a href="https://pypi.org/project/redispatcher" target="_blank">
    <img src="https://img.shields.io/pypi/v/redispatcher?color=%2334D058" alt="pypi" />
  </a>
  <a href="https://pypi.org/project/redispatcher" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/redispatcher?color=%23334D058" alt="Supported Python Versions: 3.8, 3.9, 3.10" />
  </a>
  <a href="https://github.com/rafalstapinski/redispatcher/blob/master/LICENSE" target="_blank">
    <img src="https://img.shields.io/pypi/l/redispatcher?color=%23334D058" alt="MIT License" />
  </a>
</p>


redispatcher is a small library that allows you to specify a pool of workers that listen to messages added to queues in Redis. This allows you to execute long running background tasks asynchronously, like sending a welcome email after a user registers.

redispatcher relies on
* `aioredis` to publish to Redis queues and for your consumers to read from Redis
* `pydantic` to validate all messages and make sure they conform to the shape you specify

### You should try redispatcher if you
* Have a redis instance
* Have a web service that needs to process long running tasks asynchronously
* Don't want to deal with setting up Rabbit and cumbersome libraries like Celery


## Overview

redispatcher can be broken down into three (ish) parts.

#### Consumer
It all begins with a consumer. A consumer is just a class that defines the structure of the mssages it will be listening for and a function that implements the logic for processing that message.

#### Publishing
Every consumer you define will provide you with an easy `publish` method that you can use to queue up messages. Because we use Pydantic, it will validate and ensure that any messages you send/receive have to be formatted correctly. 

#### Consumer Pool
A consumer pool is a separate process that listens for all relevant messages queued up in Redis and dispatches them to the designated consumers to be processed.


## Install
```bash
$ pip install redispatcher
```

### Basic Consumer
```python
# my_consumer.py
from redispatcher import BaseConsumer

class MyConsumer(BaseConsumer):

    QUEUE = "my-queue-key"

    class Message(BaseConsumer.Message):
        email: str
        name: str
        registered: bool
    
    async def process_message(self, message: Message):
        print(f"processing message {message}")
        ...

```

### Running your consumers in a pool

#### Defining your pool
```python
# pool.py
from redispatcher import ConsumerPool, RedispatcherConfig, ConsumerConfig

from my_consumer import MyConsumer

config = RedispatcherConfig(
    redis_dsn="rediss://", # if not provided, will read from env
    consumers=[
        ConsumerConfig(
            consumer_class=MyConsumer
        )
    ]
)

if __name__ == "__main__":
    consumer_pool = ConsumerPool(config)
    consumer_pool.start() 
```

```bash
$ python pool.py
```

### Publishing messages to your pool
```python
# endpoint.py

from my_consumer import MyConsumer
from clients import my_aioredis_client

@app.post("/signup")
async def signup()
    # queue up work to send a welcome email while we continue with the rest of our endpoint logic
    await MyConsumer.publish(MyConsumer.Message(email=..., name=..., registered=True), my_aioredis_client)
```


### Advanced usage

We built redispatcher with a couple of handy utilities, but kept it as minimal as possible for your own consumers to be subclassed and implement any logging/tracing/etc logic yourself. 

Take a look at `examples/nicer_consumer.py` and `examples/example_publisher.py` for some examples of what's possible.


### Contributing

If you have a suggestion on how to improve redispatcher or experience a bug file an issue at <https://github.com/rafalstapinski/redispatcher/issues>.

If you want to contribute, open a PR at <https://github.com/rafalstapinski/redispatcher>.

PyPi: <https://pypi.org/project/redispatcher/>
