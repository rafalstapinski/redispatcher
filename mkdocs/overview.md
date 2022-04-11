
## Overview

redispatcher can be broken down into three (ish) parts.

#### Consumer
It all begins with a consumer. A consumer is just a class that defines the structure of the mssages it will be listening for and a function that implements the logic for processing that message.

#### Publishing
Every consumer you define will provide you with an easy `publish` method that you can use to queue up messages. Because we use Pydantic, it will validate and ensure that any messages you send/receive have to be formatted correctly. 

#### Consumer Pool
A consumer pool is a separate process that listens for all relevant messages queued up in Redis and dispatches them to the designated consumers to be processed.
