# from pytest_redis import factories

# redis_proc = factories.redis_proc(executable="/opt/homebrew/bin/redis-server", port=None)
# redis = factories.redisdb("redis_proc")
from redis.client import Redis


def test_connect(redis: Redis):
    ...
