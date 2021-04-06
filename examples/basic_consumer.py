import asyncio
import os

from elasticapm.base import Client as ElasticAPMClient
from elasticapm.traces import Transaction, execution_context
from elasticapm.utils.disttracing import TraceParent

from redispatcher import BaseConsumer

"""
This is a barebones consumer. Nothing fancy here.
"""


class BasicConsumer(BaseConsumer):

    # Define what redis key our queue will live on
    QUEUE = "redispatcher-basic-consumer"

    # Define the message body this worker will process
    class Message(BaseConsumer.Message):
        a: str
        b: int
        c: bool

    # Define the logic which will run for each received message
    async def process_message(self, message: Message, headers: BaseConsumer.Headers):
        print(f"basic consumer processing message {message} {headers}")
        # simulate some IO blocking operation
        await asyncio.sleep(2)
        print("basic consumer done processing message")
