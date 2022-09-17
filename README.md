# redispatcher

<a href="https://rafalstapinski.github.io/redispatcher">
  <img src="https://rafalstapinski.github.io/redispatcher/img/logo.svg" alt="redispatcher logo" />
</a>

<p align="center">
  <strong>
    <em>
        Dispatch and run distributed work asynchronously, brokered by Redis
    </em>
  </strong>
</p>

---

**Documentation**: <a href="https://rafalstapinski.github.io/redispatcher">https://rafalstapinski.github.io/redispatcher</a>

**Source Code**: <a href="https://github.com/rafalstapinski/redispatcher">https://github.com/rafalstapinski/redispatcher</a>

---

<p align="center">
  <a href="https://github.com/rafalstapinski/redispatcher/actions/workflows/test.yml" target="_blank">
    <img src="https://github.com/rafalstapinski/redispatcher/actions/workflows/test.yml/badge.svg" alt="Test Status" />
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

redispatcher is a library and daemon for scheduling work and running it asynchronously (like <a href="https://github.com/celery/celery" >Celery</a> or <a href="https://github.com/bogdaBogdanp/dramatiq">dramatiq</a>). It allows you to execute background tasks asynchronously, like sending a welcome email after a user registers.


## Features
* Full intellisense support across your code, despite a distributed workload
* Easier and faster to set up and integrate than alternatives
* Super low overhead and completely non-blocking, thanks to `asyncio`

### Dependencies
* `aioredis` to publish to Redis queues and for your consumers to read from Redis
* `pydantic` to validate all messages and make sure they conform to the shape you specify


## Installation
Install with `poetry`
```bash
$ poetry add redispatcher
```
or with `pip`
```bash
$ pip install redispatcher
```
## Basic Usage
### Running your workers
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

```python
# dispatcher.py
from redispatcher import Redispatcher, RedispatcherConfig, ConsumerConfig

from my_consumer import MyConsumer

config = RedispatcherConfig(
    redis_dsn="rediss://",
    consumers=[
        ConsumerConfig(
            consumer_class=MyConsumer
        )
    ]
)

if __name__ == "__main__":
    dispatcher = Redispatcher(config)
    dispatcher.start() 
```

```bash
$ python dispatcher.py
```

### Publishing messages
```python
# endpoint.py

from my_consumer import MyConsumer
from clients import my_aioredis_client

@app.post("/signup")
async def signup()
    ...
    await MyConsumer.publish(MyConsumer.Message(email=..., name=..., registered=True), my_aioredis_client)
    ...
```

### Contributing

If you have a suggestion on how to improve redispatcher or experience a bug file an issue at <https://github.com/rafalstapinski/redispatcher/issues>.

If you want to contribute, open a PR at <https://github.com/rafalstapinski/redispatcher>.

PyPi: <https://pypi.org/project/redispatcher/>
