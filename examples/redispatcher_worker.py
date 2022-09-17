from examples.basic_consumer import BasicConsumer
from examples.nicer_consumer import NicerConsumer
from redispatcher import ConsumerConfig, Redispatcher, RedispatcherConfig

# We specify our consumers. Let's throw both the Nicer and Basic consumers into the
# same pool for the heck of it, but in production we only ever use the same type of
# consumer - in our case ones very similar to NicerConsumer, i.e. those subclassed
# from something similar to OurBaseConsumer

# We don't need to specify the `redis_dsn` property as pydantic.BaseSettings
# pulls REDIS_DSN from the environment automatically. You can obviously
# pass one in explicitly if, for example, you have different pools running
# with different Redises as different brokers

config = RedispatcherConfig(
    consumers=[ConsumerConfig(consumer_class=NicerConsumer), ConsumerConfig(consumer_class=BasicConsumer)]
)

if __name__ == "__main__":
    consumer_pool = Redispatcher(config)
    consumer_pool.start()
