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

## What is redispatcher

redispatcher allows you to dispatch work that needs to be done in a process separate from your main program loop. This is useful in cases when you need to process some long running work that doesn't necessarily need to be done synchronously within your code. A classic example of this is sending a welcome email to a user as they sign up for your service. It's not necessary to wait for the results of sending an email, and it may take a few seconds to do so. redispatcher lets you fire-and-forget this work (as a message put into a Redis server) and have it be executed in the background, asynchronously, in a separate process (or machine) entirely.

redispatcher comes in two parts:
1. A library that lets you define workers, define strongly typed messages sent to workers, and provides helper functions to facilitate dispatching that work
2. A daemon that runs your workers in a pool, consistently listening for any incoming messages to be processed


## Why use it

There are certainly other solutions for orchestrating distributed workers. redispatcher aims to be super lightweight, very fast and simple to set up (there are many free cloud-hosted Redis solutions available), and has robust type validation and intellisense support.
## Features
* Full intellisense support across your code, despite a distributed workload
* Strongly typed message contract between your publishing code and consumer
* Minimal boilerplate required to setup and start publishing compared than most alternatives
* Minimal performance overhead and completely non-blocking, thanks to `asyncio` (and works with alternatives like `uvloop`)

### Dependencies
* `aioredis` is used under the hood to publish message to and read messages from Redis
* `pydantic` is used to to validate messages conform to your strongly typed contracts


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
### Defining your worker
```python
from redispatcher import BaseConsumer

class SendWelcomeEmail(BaseConsumer):

    QUEUE = "send-welcome-email"

    class Message(BaseConsumer.Message):
        email: str
        name: str
    
    async def process_message(self, message: Message):
        # construct an email and send it to the `message.email` address
```

### Dispatching work
```python
from clients import my_aioredis_client

@app.post("/register")
async def register(...)
    ...
    message = SendWelcomeEmail.Message(email=..., name=..., registered=True)
    await SendWelcomeEmail.dispatch(message, my_aioredis_client)
    ...
```

### Running redispatcher
```python
from redispatcher import Redispatcher, RedispatcherConfig, ConsumerConfig

config = RedispatcherConfig(
    redis_dsn="redis://localhost:6379/0",
    consumers=[
        ConsumerConfig(
            consumer_class=SendWelcomeEmail,
            count=2
        )
    ]
)

if __name__ == "__main__":
    dispatcher = Redispatcher(config)
    dispatcher.start() 
```


### Contributing

`redispatcher` is already used in production, but is still in its infancy.

If you find a bug, <a href="https://github.com/rafalstapinski/redispatcher/issues/new">open an issue</a> with a detailed description and steps to reproduce.

If you're looking for a feature, <a href="https://github.com/rafalstapinski/redispatcher/issues/new">open an issue</a> with a detailed description and use case. Feel free <a href="https://github.com/rafalstapinski/redispatcher/pulls">open a pull request</a> if you want to contribure directly!
