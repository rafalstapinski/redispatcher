import asyncio
import sys

from elasticapm.base import DummyClient as APMClient
from elasticapm.traces import Transaction, execution_context
from elasticapm.utils.disttracing import TraceParent

from redispatcher import BaseConsumer

"""
When we use redispatcher, we create a new BaseConsumer all of our
consumers inherit from. This will implement base behavior across 
our monorepo that is specific to that project. Things like
 * tracing
 * logging
 * retry logic
"""


class OurBaseConsumer(BaseConsumer):

    apm_client: APMClient

    # This is sent along with every message. We use it for APM tracing
    class Headers(BaseConsumer.Headers):
        traceparent: str

    def __init__(self):
        super().__init__()
        self.apm_client = APMClient({"SERVICE_NAME": self.QUEUE})

    # Implement custom headers, we use elastic-apm to pass on the traceparent
    @classmethod
    def headers(cls) -> Headers:
        transaction: Transaction = execution_context.get_transaction()
        trace_parent: TraceParent = transaction.trace_parent
        return cls.Headers(traceparent=trace_parent.to_string())

    # We stub this out and where the individual consumer logic will live
    async def run(self, message: BaseConsumer.Message):
        raise NotImplementedError

    # Define logic that will run for all our consumers
    async def process_message(self, message: BaseConsumer.Message, headers: Headers):

        # Start a trace
        self.apm_client.begin_transaction("redispatcher", TraceParent.from_string(headers.traceparent))
        result = "OK"

        # Try to run, have some custom exception logic too like finishing trace result
        try:
            await self.run(message)
        except Exception:
            self.apm_client.capture_exception(exc_info=sys.exc_info())
            result = "ERROR"
        finally:
            self.apm_client.end_transaction(self.QUEUE, result=result)


# Subclasses to use the custom shared loging in OurBaseConsumer
class NicerConsumer(OurBaseConsumer):

    # This defines the key on which our redis messager queue will live on
    QUEUE = "redispatcher-nice-consumer"

    class Message(OurBaseConsumer.Message):
        yeet: str

    async def run(self, message: Message):
        print(f"nice consumer processing message {message}")
        # lets imitate some IO blocking operation
        await asyncio.sleep(2)
        print(f"nice consumer done processing message")
