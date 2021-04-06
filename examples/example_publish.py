import asyncio
import os

import aioredis
from elasticapm.base import DummyClient as APMClient

from examples import basic_consumer, nicer_consumer


async def run():

    BasicConsumer = basic_consumer.BasicConsumer
    NicerConsumer = nicer_consumer.NicerConsumer

    redis_pool = await aioredis.create_redis_pool(os.environ["REDIS_DSN"])

    # Publish a basic message to a basic consumer

    print("Publishing to our basic consumer")
    await BasicConsumer.publish(message_body=BasicConsumer.Message(a="basic", b=12, c=True), redis_client=redis_pool)

    # Publish a message with with APM tracing to our nicer consumer. We start a parent
    # transaction so our NicerConsumer is able to read the trace headers and start its
    # own child transaction

    apm_client = APMClient({"SERVICE_NAME": "publisher-service"})
    apm_client.begin_transaction("http")
    print("Publishing to our nicer consumer")
    await NicerConsumer.publish(message_body=NicerConsumer.Message(yeet="nice"), redis_client=redis_pool)
    apm_client.end_transaction("OK")


if __name__ == "__main__":
    asyncio.run(run())
